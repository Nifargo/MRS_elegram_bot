"""Детерміновані запобіжники навколо виклику Groq.

Правила в промпті обходяться і межею безпеки не є — нею є перевірки в цьому
модулі. Модуль лишається синхронним і без IO: відправку повідомлень робить той,
хто його викликає.
"""
import logging
import re

from config import ALTEGIO_BOOKING_WIDGET_URL, HELP_PHONE

logger = logging.getLogger(__name__)

MAX_INPUT_CHARS = 1000

_AMOUNT_RE = re.compile(r"(\d[\d\s\u00a0.,]*)\s*(?:грн|гривн\w*|гривен\w*|₴)", re.IGNORECASE)
_URL_RE = re.compile(r"https?://\S+")
_ALLOWED_URL_PREFIXES = (ALTEGIO_BOOKING_WIDGET_URL,)

AI_UNAVAILABLE_TEXT = (
    "Зараз не можу відповісти на це питання 🙁\n"
    f"Зателефонуйте, будь ласка, в салон: {HELP_PHONE} — там підкажуть одразу."
)


def amounts_in(text: str) -> set[int]:
    """Усі суми в гривнях, зведені до цілих. «1 300 грн» і «1300грн» дають те саме."""
    found = set()
    for raw in _AMOUNT_RE.findall(text):
        digits = re.sub(r"\D", "", raw)
        if digits:
            found.add(int(digits))
    return found


def unknown_amounts(reply: str, allowed: frozenset[int]) -> set[int]:
    """Суми з відповіді моделі, яких не було в контексті. Порожня множина — все гаразд."""
    return amounts_in(reply) - set(allowed)


def strip_foreign_links(text: str) -> str:
    """Прибрати посилання поза білим списком: модель не має інтернету, але текст
    із даних міг би схилити її вивести чуже посилання."""
    def keep(match: re.Match) -> str:
        return match.group(0) if match.group(0).startswith(_ALLOWED_URL_PREFIXES) else ""

    return " ".join(_URL_RE.sub(keep, text).split())


def price_fallback(price_lines: list[str]) -> str:
    """Відповідь замість тієї, яку відхилила перевірка сум."""
    if not price_lines:
        return AI_UNAVAILABLE_TEXT
    return ("Щоб не помилитись із сумою, ось актуальні ціни:\n"
            + "\n".join(price_lines)
            + f"\n\nОстаточну суму підтвердить майстер при огляді. Питання — {HELP_PHONE}")
