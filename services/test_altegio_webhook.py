"""process_record() reconcile path: жоден бренд-новий-і-вже-скасований запис
(webhook, якого ніколи не було, підхоплений щоденною звіркою) не повинен
слати клієнту підтвердження "Вас записано"."""
import unittest
from unittest.mock import patch

from services import altegio_webhook


class ProcessRecordTest(unittest.TestCase):
    def _record(self, **overrides):
        data = {
            "id": 1,
            "datetime": "2026-08-10 12:00:00",
            "seance_length": 3600,
            "services": [{"id": 5, "title": "Стрижка"}],
            "client": {"phone": "+380501234567"},
        }
        data.update(overrides)
        return data

    @patch("services.altegio_webhook.notifications")
    @patch("services.altegio_webhook.db")
    def test_new_cancelled_record_sends_no_confirmation(self, db, notifications):
        db.get_tracked_record.return_value = None
        db.get_client_by_phone.return_value = {"id": 1, "tg_user_id": 42}
        db.get_pets_by_client.return_value = []

        altegio_webhook.process_record(self._record(attendance=-1), "company1")

        notifications.send_telegram_message.assert_not_called()
        notifications.cancel_visit_notifications.assert_called_once_with(1)

    @patch("services.altegio_webhook.notifications")
    @patch("services.altegio_webhook.db")
    def test_new_active_record_sends_confirmation(self, db, notifications):
        db.get_tracked_record.return_value = None
        db.get_client_by_phone.return_value = {"id": 1, "tg_user_id": 42}
        db.get_pets_by_client.return_value = []

        altegio_webhook.process_record(self._record(), "company1")

        notifications.send_telegram_message.assert_called_once()
        notifications.schedule_visit_notifications.assert_called_once()


if __name__ == "__main__":
    unittest.main()
