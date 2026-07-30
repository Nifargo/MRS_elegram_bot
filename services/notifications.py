"""Створення та відправка сповіщень.

Відправка йде напряму через Telegram Bot API (requests, синхронно) —
cron-диспетчер працює у Flask-потоці без event loop-а, тож так найпростіше
і найнадійніше.
"""
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, TELEGRAM_TOKEN
from db import client as db

logger = logging.getLogger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")
FORM_INCOMPLETE_HOUR = 21  # о котрій годині (Київ) нагадувати адмінам про незаповнені анкети
BOOKING_INCOMPLETE_HOUR = 18  # о котрій годині (Київ) нагадувати адмінам про незавершений запис

_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# PythonAnywhere проксі інколи віддає транзиентний 502/503/504 на вихідні виклики
# api.telegram.org (те саме джерело, що змусило handlers/common.with_retry() ретраїти
# async-виклики) — cron-диспетчер шле напряму через requests, тож ретраї тут через
# Session-level adapter, а не через ручний цикл.
_session = requests.Session()
_session.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(
        total=6,
        backoff_factor=1.5,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset(["POST"]),
    )),
)


def send_telegram_message(chat_id: int, text: str, message_thread_id: int | None = None) -> bool:
    """Надіслати повідомлення напряму через Bot API (з ретраями на транзиентні 502/503/504). Повертає True при успіху."""
    payload = {"chat_id": chat_id, "text": text}
    if message_thread_id is not None:
        payload["message_thread_id"] = message_thread_id
    try:
        response = _session.post(f"{_API_URL}/sendMessage", json=payload, timeout=15)
        if not response.ok:
            logger.error(f"Telegram sendMessage {chat_id}: HTTP {response.status_code} {response.text[:200]}")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"Telegram sendMessage {chat_id}: {e}")
        return False


def notify_admins(text: str) -> bool:
    """Надіслати повідомлення в адмін-топік групи. True, якщо дійшло."""
    if not ADMIN_GROUP_CHAT_ID:
        logger.warning("ADMIN_GROUP_CHAT_ID не задано — сповіщення адмінам нікуди слати")
        return False
    return send_telegram_message(ADMIN_GROUP_CHAT_ID, text, message_thread_id=ADMIN_TOPIC_ID)


async def notify_admins_async(bot, text: str) -> None:
    """Те саме, але з async-хендлера — через bot, щоб не блокувати event loop."""
    if not ADMIN_GROUP_CHAT_ID:
        logger.warning("ADMIN_GROUP_CHAT_ID не задано — сповіщення адмінам нікуди слати")
        return
    try:
        await bot.send_message(chat_id=ADMIN_GROUP_CHAT_ID, text=text, message_thread_id=ADMIN_TOPIC_ID)
    except Exception as e:
        logger.error(f"Не вдалося сповістити адмін-топік {ADMIN_GROUP_CHAT_ID}: {e}")


def schedule_form_incomplete(client_id: int) -> None:
    """Запланувати перевірку 'клієнт не заповнив анкету' на сьогодні 21:00 (Київ).

    Якщо 21:00 вже минула — на завтра. Cron перевірить registration_done
    і сповістить адмінів, лише якщо анкета досі не заповнена.
    """
    now = datetime.now(KYIV_TZ)
    send_after = now.replace(hour=FORM_INCOMPLETE_HOUR, minute=0, second=0, microsecond=0)
    if send_after <= now:
        send_after += timedelta(days=1)
    db.create_notification(client_id, "form_incomplete", send_after.isoformat())


def schedule_booking_incomplete(client_id: int) -> None:
    """Запланувати перевірку 'клієнт почав запис, але не завершив' на сьогодні 18:00 (Київ).

    Якщо 18:00 вже минула — на завтра. Не дублює, якщо для клієнта вже є
    pending-сповіщення цього типу (наприклад, кілька спроб запису за день).
    """
    if db.has_pending_notification(client_id, "booking_incomplete"):
        return
    now = datetime.now(KYIV_TZ)
    send_after = now.replace(hour=BOOKING_INCOMPLETE_HOUR, minute=0, second=0, microsecond=0)
    if send_after <= now:
        send_after += timedelta(days=1)
    db.create_notification(client_id, "booking_incomplete", send_after.isoformat())