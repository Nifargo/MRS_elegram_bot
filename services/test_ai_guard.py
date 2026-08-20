import unittest

from services import ai_guard

ALLOWED = frozenset({1300, 2400})


class AmountsTest(unittest.TestCase):
    def test_plain_amount_allowed(self):
        self.assertEqual(ai_guard.unknown_amounts("Комплекс — 1300 грн", ALLOWED), set())

    def test_invented_amount_detected(self):
        self.assertEqual(ai_guard.unknown_amounts("Буде 999 грн", ALLOWED), {999})

    def test_number_formats_normalized(self):
        for text in ("1 300 грн", "1300грн", "1\u00a0300 гривень", "1,300 грн"):
            with self.subTest(text=text):
                self.assertEqual(ai_guard.amounts_in(text), {1300})

    def test_prefix_hryvnia_and_uah_detected(self):
        self.assertEqual(ai_guard.amounts_in("від ₴1300 до ₴2400"), {1300, 2400})
        self.assertEqual(ai_guard.unknown_amounts("Комплекс 999 UAH", ALLOWED), {999})
        self.assertEqual(ai_guard.unknown_amounts("Буде ₴999", ALLOWED), {999})

    def test_sum_of_two_real_prices_rejected(self):
        # Свідоме рішення спеки: підсумки заборонені, ціни перелічуються по позиціях.
        self.assertEqual(ai_guard.unknown_amounts("Разом 3700 грн", ALLOWED), {3700})

    def test_reply_without_amounts_passes(self):
        self.assertEqual(ai_guard.unknown_amounts("Чекаємо вас у салоні!", ALLOWED), set())

    def test_number_without_currency_ignored(self):
        self.assertEqual(ai_guard.unknown_amounts("Стрижка триває 90 хвилин", ALLOWED), set())


class LinksTest(unittest.TestCase):
    def test_widget_link_kept(self):
        text = f"Записатись: {ai_guard.ALTEGIO_BOOKING_WIDGET_URL}"
        self.assertIn(ai_guard.ALTEGIO_BOOKING_WIDGET_URL, ai_guard.strip_foreign_links(text))

    def test_widget_link_kept_with_trailing_period(self):
        text = f"Записатись тут: {ai_guard.ALTEGIO_BOOKING_WIDGET_URL}."
        cleaned = ai_guard.strip_foreign_links(text)
        self.assertIn(ai_guard.ALTEGIO_BOOKING_WIDGET_URL, cleaned)

    def test_foreign_link_removed(self):
        cleaned = ai_guard.strip_foreign_links("Дивіться https://evil.example/promo тут")
        self.assertNotIn("evil.example", cleaned)

    def test_evil_url_in_query_removed(self):
        poisoned = f"{ai_guard.ALTEGIO_BOOKING_WIDGET_URL}?u=https://evil.com/steal"
        cleaned = ai_guard.strip_foreign_links(f"Запис: {poisoned}")
        self.assertNotIn("evil.com", cleaned)
        self.assertNotIn("://", cleaned)

    def test_evil_url_glued_removed(self):
        poisoned = f"{ai_guard.ALTEGIO_BOOKING_WIDGET_URL}https://evil.com/steal"
        cleaned = ai_guard.strip_foreign_links(f"Запис: {poisoned}")
        self.assertNotIn("evil.com", cleaned)

    def test_newlines_preserved_without_links(self):
        text = "Прайс:\n- Комплекс 1300 грн\n- Ванна 900 грн"
        self.assertEqual(ai_guard.strip_foreign_links(text), text)


class RateLimitTest(unittest.TestCase):
    def setUp(self):
        ai_guard.reset_state()

    def test_allows_up_to_limit(self):
        for _ in range(ai_guard.AI_RATE_LIMIT):
            self.assertTrue(ai_guard.allow_message(1, now=100.0))
        self.assertFalse(ai_guard.allow_message(1, now=100.0))

    def test_window_slides(self):
        for _ in range(ai_guard.AI_RATE_LIMIT):
            ai_guard.allow_message(1, now=100.0)
        later = 100.0 + ai_guard.RATE_WINDOW_SECONDS + 1
        self.assertTrue(ai_guard.allow_message(1, now=later))

    def test_users_counted_separately(self):
        for _ in range(ai_guard.AI_RATE_LIMIT):
            ai_guard.allow_message(1, now=100.0)
        self.assertTrue(ai_guard.allow_message(2, now=100.0))


class GuardTripTest(unittest.TestCase):
    def setUp(self):
        ai_guard.reset_state()

    def test_alerts_after_threshold(self):
        for _ in range(ai_guard.GUARD_ALERT_THRESHOLD - 1):
            self.assertFalse(ai_guard.record_guard_trip(now=100.0))
        self.assertTrue(ai_guard.record_guard_trip(now=100.0))

    def test_no_second_alert_within_hour(self):
        for _ in range(ai_guard.GUARD_ALERT_THRESHOLD):
            ai_guard.record_guard_trip(now=100.0)
        for _ in range(ai_guard.GUARD_ALERT_THRESHOLD):
            self.assertFalse(ai_guard.record_guard_trip(now=200.0))


class QuotaStateTest(unittest.TestCase):
    def setUp(self):
        ai_guard.reset_state()

    def test_collects_distinct_users(self):
        ai_guard.record_quota_block(1, "rate limit reached")
        ai_guard.record_quota_block(1, "rate limit reached")
        ai_guard.record_quota_block(2, "rate limit reached")
        users, error = ai_guard.quota_report()
        self.assertEqual(users, {1, 2})
        self.assertEqual(error, "rate limit reached")

    def test_clear_empties_report(self):
        ai_guard.record_quota_block(1, "boom")
        ai_guard.clear_quota_report()
        self.assertEqual(ai_guard.quota_report(), (set(), ""))

    def test_reset_state_clears_all(self):
        for _ in range(ai_guard.AI_RATE_LIMIT):
            ai_guard.allow_message(1, now=100.0)
        for _ in range(ai_guard.GUARD_ALERT_THRESHOLD):
            ai_guard.record_guard_trip(now=100.0)
        ai_guard.record_quota_block(1, "boom")
        ai_guard.reset_state()
        self.assertTrue(ai_guard.allow_message(1, now=100.0))
        self.assertFalse(ai_guard.record_guard_trip(now=100.0))
        self.assertEqual(ai_guard.quota_report(), (set(), ""))


class FallbackTest(unittest.TestCase):
    def test_price_fallback_lists_real_prices(self):
        text = ai_guard.price_fallback(["- Комплекс — 1300 грн"])
        self.assertIn("1300 грн", text)
        self.assertIn(ai_guard.HELP_PHONE, text)
        self.assertIn("Остаточну суму підтвердить майстер", text)

    def test_price_fallback_without_prices_gives_phone(self):
        text = ai_guard.price_fallback([])
        self.assertIn(ai_guard.HELP_PHONE, text)
        self.assertNotIn("грн", text)


if __name__ == "__main__":
    unittest.main()
