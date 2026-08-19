"""send_telegram_document(): файл іде в sendDocument як multipart, помилка HTTP → False."""
import unittest
from unittest.mock import MagicMock, patch

from services import notifications


class SendDocumentTest(unittest.TestCase):
    @patch("services.notifications._session")
    def test_sends_file_as_multipart(self, session):
        session.post.return_value = MagicMock(ok=True)

        result = notifications.send_telegram_document(
            42, "backup.json", b'{"a": 1}', caption="бекап",
        )

        self.assertTrue(result)
        self.assertTrue(session.post.call_args.args[0].endswith("/sendDocument"))
        kwargs = session.post.call_args.kwargs
        self.assertEqual(kwargs["data"], {"chat_id": 42, "caption": "бекап"})
        self.assertEqual(kwargs["files"]["document"][0], "backup.json")
        self.assertEqual(kwargs["files"]["document"][1], b'{"a": 1}')

    @patch("services.notifications._session")
    def test_http_error_returns_false(self, session):
        session.post.return_value = MagicMock(ok=False, status_code=400, text="Bad Request")

        result = notifications.send_telegram_document(42, "backup.json", b"{}")

        self.assertFalse(result)

    @patch("services.notifications._session")
    def test_caption_omitted_when_not_given(self, session):
        session.post.return_value = MagicMock(ok=True)

        notifications.send_telegram_document(42, "backup.json", b"{}")

        self.assertEqual(session.post.call_args.kwargs["data"], {"chat_id": 42})


if __name__ == "__main__":
    unittest.main()
