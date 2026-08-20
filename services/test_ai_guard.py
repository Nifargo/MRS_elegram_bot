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
                self.assertEqual(ai_guard.unknown_amounts(text, ALLOWED), set())

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

    def test_foreign_link_removed(self):
        cleaned = ai_guard.strip_foreign_links("Дивіться https://evil.example/promo тут")
        self.assertNotIn("evil.example", cleaned)


class FallbackTest(unittest.TestCase):
    def test_price_fallback_lists_real_prices(self):
        text = ai_guard.price_fallback(["- Комплекс — 1300 грн"])
        self.assertIn("1300 грн", text)
        self.assertIn(ai_guard.HELP_PHONE, text)

    def test_price_fallback_without_prices_gives_phone(self):
        text = ai_guard.price_fallback([])
        self.assertIn(ai_guard.HELP_PHONE, text)
        self.assertNotIn("грн", text)


if __name__ == "__main__":
    unittest.main()
