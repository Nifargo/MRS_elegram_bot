import asyncio
import logging
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
        logging.getLogger("groq_client").setLevel(logging.CRITICAL)

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

    def test_other_error_returns_apology(self):
        with mock.patch.object(groq_client.client.chat.completions, "create",
                               side_effect=RuntimeError("boom")):
            reply = asyncio.run(groq_client.get_response(1, "привіт", ""))
        self.assertIn("помилка", reply.lower())


if __name__ == "__main__":
    unittest.main()
