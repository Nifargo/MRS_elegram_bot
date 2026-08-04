"""Фаза 7, п.1: день народження улюбленця — щоденне привітання (без знижки, поки що).

Дедуп не потрібен: збіг місяця/дня — подія одного календарного дня, а
_run_daily_tasks() і так гарантує не більше одного запуску на добу (cron_state).
"""
import logging

from datetime import datetime

from db import client as db
from services import notifications
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)


def send_birthday_greetings() -> bool:
    """Привітати клієнтів, чий улюбленець народився сьогодні (без урахування року).

    Повертає True лише якщо всі привітання надіслані без збоїв (той самий
    контракт, що vaccine_sync.sync_vaccine_dates()).
    """
    today = datetime.now(KYIV_TZ).date()
    pets = db.get_pets_with_birth_date()

    sent = 0
    all_ok = True
    for pet in pets:
        birth_date = datetime.strptime(pet["birth_date"], "%Y-%m-%d").date()
        if (birth_date.month, birth_date.day) != (today.month, today.day):
            continue

        client = db.get_client_by_id(pet["client_id"])
        if client is None:
            continue

        text = f"🎂 З днем народження, {pet['name']}! Бажаємо здоров'я та веселих пригод! 🐾"
        if notifications.send_telegram_message(client["tg_user_id"], text):
            sent += 1
        else:
            all_ok = False

    logger.info(f"🎂 Привітання з днем народження: перевірено {len(pets)}, надіслано {sent}{'' if all_ok else ' (є збої — повтор на наступному тику)'}")
    return all_ok
