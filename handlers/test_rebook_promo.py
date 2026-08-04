"""handle_callback(): rp_dismiss записує rebook_promo_dismissed_record_id;
чужий callback (record належить іншому tg_user_id) отримує відмову, без запису в БД."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from handlers import rebook_promo


def _update(data: str, tg_user_id: int):
    update = MagicMock()
    update.callback_query.data = data
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.effective_user.id = tg_user_id
    return update


class RebookPromoCallbackTest(unittest.IsolatedAsyncioTestCase):
    @patch("handlers.rebook_promo.db")
    async def test_dismiss_marks_client(self, db):
        db.get_tracked_record.return_value = {"client_id": 10}
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42}
        update = _update("rp_dismiss:1", 42)

        await rebook_promo.handle_callback(update, MagicMock())

        db.update_client.assert_called_once_with(10, {"rebook_promo_dismissed_record_id": 1})

    @patch("handlers.rebook_promo.db")
    async def test_foreign_record_rejected(self, db):
        db.get_tracked_record.return_value = {"client_id": 10}
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 999}
        update = _update("rp_dismiss:1", 42)

        await rebook_promo.handle_callback(update, MagicMock())

        db.update_client.assert_not_called()
        update.callback_query.edit_message_text.assert_called_once_with("Це нагадування недоступне.")

    @patch("handlers.rebook_promo.db")
    async def test_db_failure_on_dismiss_shows_retry_message(self, db):
        db.get_tracked_record.return_value = {"client_id": 10}
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42}
        db.update_client.side_effect = Exception("Supabase недоступний")
        update = _update("rp_dismiss:1", 42)

        await rebook_promo.handle_callback(update, MagicMock())

        update.callback_query.edit_message_text.assert_called_once_with(
            "⚠️ Не вдалося зберегти. Спробуйте натиснути ще раз."
        )


if __name__ == "__main__":
    unittest.main()
