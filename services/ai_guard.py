"""Детерміновані запобіжники навколо виклику Groq.

Правила в промпті обходяться і межею безпеки не є — нею є перевірки в цьому
модулі. Модуль лишається синхронним і без IO: відправку повідомлень робить той,
хто його викликає.
"""
import re
import time
from urllib.parse import urlparse

from config import ALTEGIO_BOOKING_WIDGET_URL, HELP_PHONE

MAX_INPUT_CHARS = 1000

AI_RATE_LIMIT = 15            # повідомлень на годину від одного tg_user_id
RATE_WINDOW_SECONDS = 3600
GUARD_ALERT_THRESHOLD = 5     # відхилень за годину, після яких сповіщаємо адмінів
GUARD_ALERT_WINDOW_SECONDS = 3600

_hits: dict[int, list[float]] = {}
_trips: list[float] = []
_last_trip_alert: float | None = None
_quota_affected: set[int] = set()
_quota_error: str = ""

_NUM = r"\d[\d\s\u00a0.,]*"
_CURRENCY = r"(?:грн|гривн\w*|гривен\w*|₴|uah)"

# Гілка діапазону мусить стояти першою: інакше з «900–1400 грн» видно лише
# 1400, а нижня межа — рівно те місце, де модель може занизити ціну втричі.
# Валюта після другого числа обов'язкова, тому «Йорк 2-4 кг» грошима не стане.
_AMOUNT_RE = re.compile(
    rf"(?:"
    rf"({_NUM}?)\s*[-–—]\s*({_NUM})\s*{_CURRENCY}"
    rf"|({_NUM})\s*{_CURRENCY}"
    rf"|₴\s*({_NUM})"
    rf")",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_ALLOWED_HOSTS = {urlparse(ALTEGIO_BOOKING_WIDGET_URL).netloc.lower()}

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
    if parsed.netloc.lower() not in _ALLOWED_HOSTS:
        return False
    rest = url[url.index(parsed.netloc) + len(parsed.netloc):]
    return "://" not in rest


def _keep_allowed(match: re.Match) -> str:
    return match.group(0) if _is_allowed_url(match.group(0)) else ""


def amounts_in(text: str) -> set[int]:
    """Усі суми в гривнях, зведені до цілих. «1 300 грн» і «1300грн» дають те саме.
    Діапазон «900–1400 грн» дає обидві межі.

    Кома й крапка трактуються як роздільник тисяч (не десятковий), тож
    «1300,50 грн» дасть 130050. Ціни салону — цілі, тому це свідоме спрощення.
    """
    found = set()
    for match in _AMOUNT_RE.finditer(text):
        for raw in match.groups():
            digits = re.sub(r"\D", "", raw or "")
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


def reset_state() -> None:
    """Для тестів."""
    global _last_trip_alert, _quota_error
    _hits.clear()
    _trips.clear()
    _last_trip_alert = None
    _quota_affected.clear()
    _quota_error = ""


def allow_message(tg_user_id: int, now: float | None = None) -> bool:
    """False — особистий ліміт вичерпано, Groq викликати не треба.

    Захищає спільну квоту безкоштовного Groq: без цього один активний
    користувач здатен вичерпати її для решти клієнтів.
    """
    now = time.monotonic() if now is None else now
    hits = [t for t in _hits.get(tg_user_id, []) if now - t < RATE_WINDOW_SECONDS]
    if len(hits) >= AI_RATE_LIMIT:
        _hits[tg_user_id] = hits
        return False
    hits.append(now)
    _hits[tg_user_id] = hits
    return True


def record_guard_trip(now: float | None = None) -> bool:
    """Порахувати відхилену відповідь. True — час сповістити адмінів.

    Ловить сценарій «Groq змінив модель або промпт поплив, бот тихо перейшов у
    режим вічного фолбеку»: така поломка дає стабільний потік відхилень, тож
    після перезапуску лічильник набере поріг заново за перші ж кілька
    відхилень — сповіщення прийде знову, без пам'яті про попередній прогін.
    """
    global _last_trip_alert
    now = time.monotonic() if now is None else now
    _trips[:] = [t for t in _trips if now - t < GUARD_ALERT_WINDOW_SECONDS] + [now]
    if len(_trips) < GUARD_ALERT_THRESHOLD:
        return False
    if _last_trip_alert is not None and now - _last_trip_alert < GUARD_ALERT_WINDOW_SECONDS:
        return False
    _last_trip_alert = now
    return True


def record_quota_block(tg_user_id: int, error_text: str) -> None:
    """Запам'ятати клієнта, який наткнувся на 429, для дайджесту о 18:30."""
    global _quota_error
    _quota_affected.add(tg_user_id)
    _quota_error = error_text[:200]


def quota_report() -> tuple[set[int], str]:
    """Повернути tg_user_id, що наткнулись на 429, і текст останньої помилки."""
    return set(_quota_affected), _quota_error


def clear_quota_report() -> None:
    """Скинути накопичений дайджест після підтвердженої відправки (Task 7)."""
    global _quota_error
    _quota_affected.clear()
    _quota_error = ""
