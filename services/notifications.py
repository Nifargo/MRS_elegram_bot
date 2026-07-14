"""Створення та відправка сповіщень.

Відправка йде напряму через Telegram Bot API (requests, синхронно) —
cron-диспетчер працює у Flask-потоці без event loop-а, тож так найпростіше
і найнадійніше.
"""
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from config import ADMIN_CHAT_IDS, TELEGRAM_TOKEN
from db import client as db

logger = logging.getLogger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")
FORM_INCOMPLETE_HOUR = 21  # о котрій годині (Київ) нагадувати адмінам про незаповнені анкети

_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_telegram_message(chat_id: int, text: str) -> bool:
    """Надіслати повідомлення напряму через Bot API. Повертає True при успіху."""
    try:
        response = requests.post(
            f"{_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
        if not response.ok:
            logger.error(f"Telegram sendMessage {chat_id}: HTTP {response.status_code} {response.text[:200]}")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"Telegram sendMessage {chat_id}: {e}")
        return False


def notify_admins(text: str) -> bool:
    """Надіслати повідомлення всім адміністраторам. True, якщо дійшло хоч одному."""
    if not ADMIN_CHAT_IDS:
        logger.warning("ADMIN_CHAT_IDS порожній — сповіщення адмінам нікуди слати")
        return False
    delivered = [send_telegram_message(chat_id, text) for chat_id in ADMIN_CHAT_IDS]
    return any(delivered)


async def notify_admins_async(bot, text: str) -> None:
    """Те саме, але з async-хендлера — через bot, щоб не блокувати event loop."""
    if not ADMIN_CHAT_IDS:
        logger.warning("ADMIN_CHAT_IDS порожній — сповіщення адмінам нікуди слати")
        return
    for chat_id in ADMIN_CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger.error(f"Не вдалося сповістити адміна {chat_id}: {e}")


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