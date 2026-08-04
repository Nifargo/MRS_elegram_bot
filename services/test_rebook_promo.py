"""send_rebook_promos(): клієнт з простроченим (6+ тижнів) останнім візитом і
вільним місцем "завтра" отримує промо; свіжий візит або дедуп (кулдаун/дісміс)
блокують відправку."""
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from services import rebook_promo
from services.notifications import KYIV_TZ


def _iso(days_ago: int) -> str:
    return (datetime.now(KYIV_TZ) - timedelta(days=days_ago)).isoformat()


class RebookPromoTest(unittest.TestCase):
    @patch("services.rebook_promo.notifications")
    @patch("services.rebook_promo.altegio")
    @patch("services.rebook_promo.db")
    def test_overdue_client_with_free_slot_gets_promo(self, db, altegio, notifications):
        db.get_active_tracked_records_with_ends_at.return_value = [
            {"altegio_record_id": 1, "client_id": 10, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(45)},
        ]
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42, "last_promo_at": None, "rebook_promo_dismissed_record_id": None}
        tomorrow = (datetime.now(KYIV_TZ) + timedelta(days=1)).date().isoformat()
        altegio.get_available_dates.return_value = [tomorrow]
        notifications.send_telegram_message.return_value = True

        result = rebook_promo.send_rebook_promos()

        notifications.send_telegram_message.assert_called_once()
        db.update_client.assert_called_once_with(10, {"last_promo_at": unittest.mock.ANY})
        self.assertTrue(result)

    @patch("services.rebook_promo.notifications")
    @patch("services.rebook_promo.altegio")
    @patch("services.rebook_promo.db")
    def test_recent_visit_not_overdue_skipped(self, db, altegio, notifications):
        db.get_active_tracked_records_with_ends_at.return_value = [
            {"altegio_record_id": 1, "client_id": 10, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(10)},
        ]

        rebook_promo.send_rebook_promos()

        notifications.send_telegram_message.assert_not_called()

    @patch("services.rebook_promo.notifications")
    @patch("services.rebook_promo.altegio")
    @patch("services.rebook_promo.db")
    def test_dismissed_record_skipped(self, db, altegio, notifications):
        db.get_active_tracked_records_with_ends_at.return_value = [
            {"altegio_record_id": 1, "client_id": 10, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(45)},
        ]
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42, "last_promo_at": None, "rebook_promo_dismissed_record_id": 1}

        rebook_promo.send_rebook_promos()

        notifications.send_telegram_message.assert_not_called()

    @patch("services.rebook_promo.notifications")
    @patch("services.rebook_promo.altegio")
    @patch("services.rebook_promo.db")
    def test_cooldown_active_skipped(self, db, altegio, notifications):
        db.get_active_tracked_records_with_ends_at.return_value = [
            {"altegio_record_id": 1, "client_id": 10, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(45)},
        ]
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42, "last_promo_at": _iso(2), "rebook_promo_dismissed_record_id": None}

        rebook_promo.send_rebook_promos()

        notifications.send_telegram_message.assert_not_called()

    @patch("services.rebook_promo.notifications")
    @patch("services.rebook_promo.altegio")
    @patch("services.rebook_promo.db")
    def test_one_client_db_failure_does_not_block_others(self, db, altegio, notifications):
        db.get_active_tracked_records_with_ends_at.return_value = [
            {"altegio_record_id": 1, "client_id": 10, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(45)},
            {"altegio_record_id": 2, "client_id": 11, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(46)},
        ]
        db.get_client_by_id.side_effect = [
            Exception("Supabase недоступний"),
            {"id": 11, "tg_user_id": 43, "last_promo_at": None, "rebook_promo_dismissed_record_id": None},
        ]
        tomorrow = (datetime.now(KYIV_TZ) + timedelta(days=1)).date().isoformat()
        altegio.get_available_dates.return_value = [tomorrow]
        notifications.send_telegram_message.return_value = True

        result = rebook_promo.send_rebook_promos()

        notifications.send_telegram_message.assert_called_once()
        self.assertFalse(result)

    @patch("services.rebook_promo.notifications")
    @patch("services.rebook_promo.altegio")
    @patch("services.rebook_promo.db")
    def test_no_free_slot_tomorrow_skipped(self, db, altegio, notifications):
        db.get_active_tracked_records_with_ends_at.return_value = [
            {"altegio_record_id": 1, "client_id": 10, "company_id": "c1", "location_title": "Тест", "ends_at": _iso(45)},
        ]
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42, "last_promo_at": None, "rebook_promo_dismissed_record_id": None}
        altegio.get_available_dates.return_value = []

        rebook_promo.send_rebook_promos()

        notifications.send_telegram_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
