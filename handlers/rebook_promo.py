"""Callback-кнопки на промо вільних місць (rp_dismiss/rp_snooze) — services/rebook_promo.py.

IDOR-захист той самий підхід, що handlers/rating.py: record_id у callback_data
можна підробити, тож перевіряємо, що записаний клієнт справді належить
відправнику callback-у.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from db import client as db
from handlers.common import with_retry

logger = logging.getLogger(__name__)


def _owning_client(record_id: int, tg_user_id: int) -> dict | None:
    record = db.get_tracked_record(record_id)
    if record is None or not record.get("client_id"):
        return None
    client = db.get_client_by_id(record["client_id"])
    return client if client and client.get("tg_user_id") == tg_user_id else None


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await with_retry(query.answer)
    prefix, record_id = query.data.split(":")
    record_id = int(record_id)

    client = _owning_client(record_id, update.effective_user.id)
    if client is None:
        await with_retry(query.edit_message_text, "Це нагадування недоступне.")
        return

    if prefix == "rp_dismiss":
        try:
            db.update_client(client["id"], {"rebook_promo_dismissed_record_id": record_id})
        except Exception as e:
            logger.error(f"Не вдалося зберегти дісміс rebook-промо (client_id={client['id']}): {e}", exc_info=True)
            await with_retry(query.edit_message_text, "⚠️ Не вдалося зберегти. Спробуйте натиснути ще раз.")
            return
        await with_retry(query.edit_message_text, "Гаразд, більше не нагадуватимемо про цей візит 🙌")
    elif prefix == "rp_snooze":
        await with_retry(query.edit_message_text, "Добре, нагадаємо наступного тижня 🔔")
