"""process_record(): підтвердження клієнту (не слати на вже скасований запис)
і час візиту, від якого залежать нагадування."""
import unittest
from datetime import datetime
from unittest.mock import patch

from services import altegio_webhook
from services.notifications import KYIV_TZ


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

    @patch("services.altegio_webhook.notifications")
    @patch("services.altegio_webhook.db")
    def test_winter_record_keeps_salon_wall_clock_time(self, db, notifications):
        # Altegio ставить у `datetime` offset +03:00 і в січні, коли Київ у
        # +02:00, тож опора на це поле зсувала б візит на годину раніше — разом
        # з ним і reminder_2h, і час у «🗓 Мої записи».
        db.get_tracked_record.return_value = None
        db.get_client_by_phone.return_value = {"id": 1, "tg_user_id": 42}
        db.get_pets_by_client.return_value = []
        record = self._record(date="2026-01-06 11:15:00", datetime="2026-01-06T11:15:00+03:00")

        altegio_webhook.process_record(record, "company1")

        stored = db.upsert_tracked_record.call_args.args[0]["starts_at"]
        scheduled = notifications.schedule_visit_notifications.call_args.args[2]
        self.assertEqual(_kyiv_label(datetime.fromisoformat(stored)), "06.01.2026 11:15")
        self.assertEqual(_kyiv_label(scheduled), "06.01.2026 11:15")


def _kyiv_label(dt: datetime) -> str:
    return dt.astimezone(KYIV_TZ).strftime("%d.%m.%Y %H:%M")


if __name__ == "__main__":
    unittest.main()
