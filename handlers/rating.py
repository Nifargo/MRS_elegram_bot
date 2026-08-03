"""Оцінка візиту (⭐): callback-флоу після thanks_rating.

Стан флоу — у callback_data (rt_master:<record_id>:<stars>), без
context.user_data: клієнт може мати кілька thanks_rating-промптів одночасно
(декілька недавніх візитів), і user_data, ключований лише по user_id, дав би
колізію між ними.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import GOOGLE_MAPS_REVIEW_URLS
from db import client as db
from handlers.common import with_retry
from services import notifications

logger = logging.getLogger(__name__)


def _owns_record(record_id, tg_user_id: int) -> bool:
    """callback_data приходить від клієнта Telegram і може бути підроблена
    (кастомний клієнт може відправити будь-який callback_data на чуже
    повідомлення) — без цієї перевірки хтось міг би оцінити чужий візит
    або підмінити ім'я/телефон в адмін-алерті."""
    record = db.get_tracked_record(record_id)
    if record is None:
        return False
    client = db.get_client_by_id(record["client_id"]) if record.get("client_id") else None
    return client is not None and client.get("tg_user_id") == tg_user_id


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await with_retry(query.answer)
    parts = query.data.split(":")
    prefix = parts[0]

    if prefix == "rt_master":
        _, record_id, groomer_stars = parts
        groomer_stars = int(groomer_stars)

        if not _owns_record(record_id, update.effective_user.id):
            await with_retry(query.edit_message_text, "Ця оцінка недоступна.")
            return

        if db.get_rating(record_id) is not None:
            await with_retry(query.edit_message_text, "Дякуємо, вашу оцінку вже отримано! 💛")
            return

        db.create_rating(record_id, None, groomer_stars)
        record = db.get_tracked_record(record_id)

        review_url = GOOGLE_MAPS_REVIEW_URLS.get((record or {}).get("location_title"))
        if groomer_stars == 5 and review_url:
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("⭐ Залишити відгук на Google Maps", url=review_url)
            ]])
            await with_retry(
                query.edit_message_text,
                "💛 Дякуємо за вашу оцінку! Будемо вдячні за відгук на Google Maps:", reply_markup=keyboard,
            )
        else:
            await with_retry(query.edit_message_text, "💛 Дякуємо за вашу оцінку!")

        if groomer_stars <= 3:
            client = db.get_client_by_id(record["client_id"]) if record else None
            who = (client or {}).get("name")
            phone = (client or {}).get("phone")
            text = (
                f"⚠️ Низька оцінка від {who or '—'} ({phone or '—'}):\n"
                f"Майстер: {'⭐' * groomer_stars}"
            )
            await notifications.notify_admins_async(context.bot, text)
