"""reconcile_upcoming_records(): запис, що зник з Altegio (скасований, але
Altegio просто прибрав його зі списку get_records() замість позначки), має
бути виявлений діффом і позначений cancelled."""
import unittest
from unittest.mock import patch

from services import altegio_reconcile


@patch("services.altegio_reconcile.ALTEGIO_LOCATIONS", {"ТестФілія": "company1"})
class ReconcileTest(unittest.TestCase):
    @patch("services.altegio_reconcile.notifications")
    @patch("services.altegio_reconcile.db")
    @patch("services.altegio_reconcile.process_record")
    @patch("services.altegio_reconcile.altegio")
    def test_vanished_record_marked_cancelled(self, altegio, process_record, db, notifications):
        altegio.get_records.return_value = []  # Altegio більше не знає про запис 999
        db.get_active_tracked_records_in_range.return_value = [{"altegio_record_id": 999}]

        result = altegio_reconcile.reconcile_upcoming_records()

        db.update_tracked_record_status.assert_called_once_with(999, "cancelled")
        notifications.cancel_visit_notifications.assert_called_once_with(999)
        self.assertTrue(result)

    @patch("services.altegio_reconcile.notifications")
    @patch("services.altegio_reconcile.db")
    @patch("services.altegio_reconcile.process_record")
    @patch("services.altegio_reconcile.altegio")
    def test_present_record_not_cancelled(self, altegio, process_record, db, notifications):
        altegio.get_records.return_value = [{"id": 999}]
        db.get_active_tracked_records_in_range.return_value = [{"altegio_record_id": 999}]

        altegio_reconcile.reconcile_upcoming_records()

        db.update_tracked_record_status.assert_not_called()
        notifications.cancel_visit_notifications.assert_not_called()
        process_record.assert_called_once_with({"id": 999}, "company1")


if __name__ == "__main__":
    unittest.main()
