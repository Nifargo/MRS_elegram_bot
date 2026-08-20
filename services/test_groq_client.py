import asyncio
import unittest
from unittest import mock

from groq import RateLimitError

import groq_client


def _completion(text: str):
    return mock.Mock(choices=[mock.Mock(message=mock.Mock(content=text))])


def _rate_limit_error() -> RateLimitError:
    response = mock.Mock(status_code=429, headers={}, request=mock.Mock())
    return RateLimitError("Rate limit reached", response=response, body=None)


class GroqClientTest(unittest.TestCase):
    def setUp(self):
        groq_client.chat_histories.clear()

    def test_context_block_goes_into_system_message(self):
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               return_value=_completion("ok")) as create:
            asyncio.run(groq_client.get_response(1, "скільки?", "=== ДАНІ САЛОНУ ==="))
        system = create.call_args.kwargs["messages"][0]
        self.assertEqual(system["role"], "system")
        self.assertIn("=== ДАНІ САЛОНУ ===", system["content"])

    def test_history_trimmed(self):
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               return_value=_completion("ok")):
            for i in range(groq_client.HISTORY_LIMIT):
                asyncio.run(groq_client.get_response(1, f"питання {i}", ""))
        self.assertLessEqual(len(groq_client.chat_histories[1]), groq_client.HISTORY_LIMIT)

    def test_history_window_starts_with_user(self):
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               return_value=_completion("ok")) as create:
            for i in range(6):
                asyncio.run(groq_client.get_response(1, f"питання {i}", ""))
        messages = create.call_args.kwargs["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")

    def test_rate_limit_propagates(self):
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               side_effect=_rate_limit_error()):
            with self.assertRaises(RateLimitError):
                asyncio.run(groq_client.get_response(1, "привіт", ""))

    def test_unanswered_message_removed_from_history(self):
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               side_effect=_rate_limit_error()):
            with self.assertRaises(RateLimitError):
                asyncio.run(groq_client.get_response(1, "привіт", ""))
        self.assertEqual(groq_client.chat_histories[1], [])

    def test_empty_answer_does_not_poison_history(self):
        # content=None у історії пішов би в кожен наступний запит цього клієнта
        # до перезапуску процесу.
        for completion in (_completion(None), mock.Mock(choices=[])):
            with self.subTest(completion=completion):
                groq_client.chat_histories.clear()
                with mock.patch.object(groq_client.client.chat.completions, "create",
                                       return_value=completion):
                    with self.assertLogs("groq_client", level="ERROR"):
                        reply = asyncio.run(groq_client.get_response(1, "привіт", ""))
                self.assertIn("помилка", reply.lower())
                self.assertEqual(groq_client.chat_histories[1], [])

    def test_other_error_returns_apology(self):
        user_message = "Мене звати Андрій, телефон 0671112233"
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               side_effect=RuntimeError("boom")):
            with self.assertLogs("groq_client", level="ERROR") as logs:
                reply = asyncio.run(groq_client.get_response(1, user_message, ""))
        self.assertIn("помилка", reply.lower())
        self.assertEqual(groq_client.chat_histories[1], [])
        log_text = "\n".join(logs.output)
        self.assertIn("RuntimeError", log_text)
        self.assertNotIn(user_message, log_text)
        self.assertNotIn("Андрій", log_text)
        self.assertNotIn("0671112233", log_text)


if __name__ == "__main__":
    unittest.main()
