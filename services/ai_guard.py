"""Детерміновані запобіжники навколо виклику Groq.

Правила в промпті обходяться і межею безпеки не є — нею є перевірки в цьому
модулі. Модуль лишається синхронним і без IO: відправку повідомлень робить той,
хто його викликає.
"""
import re
from urllib.parse import urlparse

from config import ALTEGIO_BOOKING_WIDGET_URL, HELP_PHONE

MAX_INPUT_CHARS = 1000

_AMOUNT_RE = re.compile(
    r"(?:"
    r"(\d[\d\s\u00a0.,]*)\s*(?:грн|гривн\w*|гривен\w*|₴|uah)"
    r"|"
    r"₴\s*(\d[\d\s\u00a0.,]*)"
    r")",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://\S+")
_ALLOWED_HOSTS = {urlparse(ALTEGIO_BOOKING_WIDGET_URL).netloc}

AI_UNAVAILABLE_TEXT = (
    "Зараз не можу відповісти на це питання 🙁\n"
    f"Зателефонуйте, будь ласка, в салон: {HELP_PHONE} — там підкажуть одразу."
)


def _is_allowed_url(url: str) -> bool:
    """Дозволений хост і жодної другої схеми в решті адреси.

    Одного `startswith` мало: `.../?u=https://evil.com` формально починається з
    нашого віджета, але веде клієнта в інше місце.
    """
    parsed = urlparse(url)
    if parsed.netloc not in _ALLOWED_HOSTS:
        return False
    rest = url[url.index(parsed.netloc) + len(parsed.netloc):]
    return "://" not in rest


def _keep_allowed(match: re.Match) -> str:
    return match.group(0) if _is_allowed_url(match.group(0)) else ""


def amounts_in(text: str) -> set[int]:
    """Усі суми в гривнях, зведені до цілих. «1 300 грн» і «1300грн» дають те саме.

    Кома й крапка трактуються як роздільник тисяч (не десятковий), тож
    «1300,50 грн» дасть 130050. Ціни салону — цілі, тому це свідоме спрощення.
    """
    found = set()
    for match in _AMOUNT_RE.finditer(text):
        raw = match.group(1) or match.group(2)
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
    cleaned = _URL_RE.sub(_keep_allowed, text)
    if cleaned == text:
        return text
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return "\n".join(line.strip() for line in cleaned.split("\n")).strip()


def price_fallback(price_lines: list[str]) -> str:
    """Відповідь замість тієї, яку відхилила перевірка сум."""
    if not price_lines:
        return AI_UNAVAILABLE_TEXT
    return ("Щоб не помилитись із сумою, ось актуальні ціни:\n"
            + "\n".join(price_lines)
            + f"\n\nОстаточну суму підтвердить майстер при огляді. Питання — {HELP_PHONE}")
