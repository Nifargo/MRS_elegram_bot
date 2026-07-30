"""Self-check: send_telegram_message() retries transient 503s via the Session-level adapter.

Run: python3 services/test_notifications_retry.py
"""
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from services import notifications

# Same shape as the production adapter but near-zero backoff, so the
# "gives up" test doesn't sleep through the real 0/1.5/3/6/12/24s schedule.
_FAST_RETRY = HTTPAdapter(max_retries=Retry(
    total=6, backoff_factor=0.01, status_forcelist=(502, 503, 504),
    allowed_methods=frozenset(["POST"]),
))


class _FlakyHandler(BaseHTTPRequestHandler):
    failures_left = 2

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        if _FlakyHandler.failures_left > 0:
            _FlakyHandler.failures_left -= 1
            self.send_response(503)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

    def log_message(self, *args):
        pass


class RetryTest(unittest.TestCase):
    def test_retries_until_success(self):
        _FlakyHandler.failures_left = 2
        server = HTTPServer(("127.0.0.1", 0), _FlakyHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            original_url = notifications._API_URL
            original_session = notifications._session
            notifications._API_URL = f"http://127.0.0.1:{port}"
            notifications._session = requests.Session()
            notifications._session.mount("http://", _FAST_RETRY)
            try:
                ok = notifications.send_telegram_message(chat_id=123, text="hi")
            finally:
                notifications._API_URL = original_url
                notifications._session = original_session
            self.assertTrue(ok)
            self.assertEqual(_FlakyHandler.failures_left, 0)
        finally:
            server.shutdown()

    def test_gives_up_after_exhausting_retries(self):
        _FlakyHandler.failures_left = 999
        server = HTTPServer(("127.0.0.1", 0), _FlakyHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            original_url = notifications._API_URL
            original_session = notifications._session
            notifications._API_URL = f"http://127.0.0.1:{port}"
            notifications._session = requests.Session()
            notifications._session.mount("http://", _FAST_RETRY)
            try:
                ok = notifications.send_telegram_message(chat_id=123, text="hi")
            finally:
                notifications._API_URL = original_url
                notifications._session = original_session
            self.assertFalse(ok)
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
