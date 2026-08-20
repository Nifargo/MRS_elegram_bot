import unittest
from datetime import datetime
from unittest import mock

from services import ai_guard, scheduler
from services.notifications import KYIV_TZ

CLIENT = {"id": 8, "tg_user_id": 111, "name": "Андрій", "phone": "+380671112233"}


def kyiv(hour: int, minute: int, day: int = 20) -> datetime:
    return datetime(2026, 8, day, hour, minute, tzinfo=KYIV_TZ)


class DigestDueTest(unittest.TestCase):
    def test_not_due_before_1830(self):
        self.assertFalse(scheduler.is_quota_digest_due(kyiv(18, 15), None))

    def test_due_at_1830(self):
        self.assertTrue(scheduler.is_quota_digest_due(kyiv(18, 30), None))

    def test_due_on_later_tick(self):
        self.assertTrue(scheduler.is_quota_digest_due(kyiv(18, 45), None))

    def test_not_due_twice_same_day(self):
        self.assertFalse(scheduler.is_quota_digest_due(kyiv(19, 0), "2026-08-20"))

    def test_due_again_next_day(self):
        self.assertTrue(scheduler.is_quota_digest_due(kyiv(19, 0, day=21), "2026-08-20"))


class QuotaDigestTest(unittest.TestCase):
    def setUp(self):
        ai_guard.reset_state()

    def test_lists_each_affected_client_once(self):
        ai_guard.record_quota_block(111, "Rate limit reached for model")
        ai_guard.record_quota_block(111, "Rate limit reached for model")
        ai_guard.record_quota_block(222, "Rate limit reached for model")
        with mock.patch.object(scheduler.db, "get_client_by_tg_id",
                               side_effect=lambda uid: CLIENT if uid == 111 else None), \
             mock.patch.object(scheduler.notifications, "notify_admins",
                               return_value=True) as notify:
            self.assertTrue(scheduler.send_quota_digest())
        text = notify.call_args.args[0]
        self.assertEqual(text.count("Андрій"), 1)
        self.assertIn("+380671112233", text)
        self.assertIn("222", text)
        self.assertIn("Rate limit reached for model", text)

    def test_supabase_failure_still_sends_ids(self):
        ai_guard.record_quota_block(111, "boom")
        with mock.patch.object(scheduler.db, "get_client_by_tg_id",
                               side_effect=Exception("Supabase недоступний")), \
             mock.patch.object(scheduler.notifications, "notify_admins",
                               return_value=True) as notify, \
             self.assertLogs(scheduler.logger, "WARNING"):
            self.assertTrue(scheduler.send_quota_digest())
        self.assertIn("111", notify.call_args.args[0])

    def test_failed_delivery_keeps_report(self):
        ai_guard.record_quota_block(111, "boom")
        with mock.patch.object(scheduler.db, "get_client_by_tg_id", return_value=CLIENT), \
             mock.patch.object(scheduler.notifications, "notify_admins", return_value=False):
            self.assertFalse(scheduler.send_quota_digest())
        self.assertEqual(ai_guard.quota_report()[0], {111})

    def test_successful_delivery_clears_report(self):
        ai_guard.record_quota_block(111, "boom")
        with mock.patch.object(scheduler.db, "get_client_by_tg_id", return_value=CLIENT), \
             mock.patch.object(scheduler.notifications, "notify_admins", return_value=True):
            scheduler.send_quota_digest()
        self.assertEqual(ai_guard.quota_report(), (set(), ""))


if __name__ == "__main__":
    unittest.main()
