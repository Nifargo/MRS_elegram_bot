"""send_birthday_greetings(): улюбленець з днем народження сьогодні (інший рік)
отримує привітання; улюбленець з іншою датою — ні."""
import unittest
from datetime import date
from unittest.mock import patch

from services import birthday


class BirthdayTest(unittest.TestCase):
    @patch("services.birthday.datetime")
    @patch("services.birthday.notifications")
    @patch("services.birthday.db")
    def test_matching_birthday_sends_greeting(self, db, notifications, mock_datetime):
        mock_datetime.now.return_value.date.return_value = date(2026, 8, 4)
        mock_datetime.strptime = __import__("datetime").datetime.strptime
        db.get_pets_with_birth_date.return_value = [
            {"id": 1, "client_id": 10, "name": "Барні", "birth_date": "2020-08-04"},
        ]
        db.get_client_by_id.return_value = {"id": 10, "tg_user_id": 42}

        result = birthday.send_birthday_greetings()

        notifications.send_telegram_message.assert_called_once()
        self.assertIn("Барні", notifications.send_telegram_message.call_args[0][1])
        self.assertTrue(result)

    @patch("services.birthday.datetime")
    @patch("services.birthday.notifications")
    @patch("services.birthday.db")
    def test_non_matching_birthday_sends_nothing(self, db, notifications, mock_datetime):
        mock_datetime.now.return_value.date.return_value = date(2026, 8, 4)
        mock_datetime.strptime = __import__("datetime").datetime.strptime
        db.get_pets_with_birth_date.return_value = [
            {"id": 1, "client_id": 10, "name": "Барні", "birth_date": "2020-08-05"},
        ]

        birthday.send_birthday_greetings()

        notifications.send_telegram_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
