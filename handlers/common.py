"""Спільні валідатори полів анкети та карток улюбленців."""
import asyncio
import logging
import re
from datetime import date, datetime

from telegram.error import NetworkError

from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

UA_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


def format_date_label(iso_date: str) -> str:
    """'2026-08-01' -> '01.08 Сб' (для кнопок вибору дати)."""
    d = date.fromisoformat(iso_date)
    return f"{d.strftime('%d.%m')} {UA_WEEKDAYS[d.weekday()]}"


def parse_iso_datetime(raw: str) -> datetime:
    """Захисний парсинг timestamptz-рядка з Supabase/Altegio (інколи із 'Z' замість offset)."""
    return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))


def to_kyiv_iso(date_str: str, time_str: str) -> str:
    """'2026-08-01', '10:00' -> aware ISO-рядок у Europe/Kyiv, для запису в timestamptz-колонку.

    Без явного offset Supabase/PostgREST трактує наївний рядок як UTC —
    запис на 10:00 за Києвом писався б у БД як 10:00 UTC (на 2-3 години пізніше,
    ніж насправді), тому offset потрібен завжди.
    """
    return datetime.fromisoformat(f"{date_str}T{time_str}:00").replace(tzinfo=KYIV_TZ).isoformat()


def normalize_phone(raw: str) -> str | None:
    """Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на український."""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 10 and digits.startswith("0"):
        digits = "38" + digits
    if len(digits) == 12 and digits.startswith("380"):
        return "+" + digits
    return None


def parse_date(text: str, allow_future: bool = False) -> date | None:
    """Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні."""
    try:
        parsed = datetime.strptime((text or "").strip(), "%d.%m.%Y").date()
    except ValueError:
        return None
    if not allow_future and parsed > date.today():
        return None
    return parsed


def parse_weight(text: str) -> float | None:
    """Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–120."""
    try:
        weight = float((text or "").strip().replace(",", "."))
    except ValueError:
        return None
    if not 0.1 <= weight <= 120:
        return None
    return round(weight, 2)


async def with_retry(func, *args, attempts: int = 7, delay: float = 1.5, **kwargs):
    """Викликати Telegram-запит (reply_text/reply_location/...) з повторами.

    Проксі PythonAnywhere інколи віддає транзиентний 503 на вихідні виклики
    api.telegram.org — без повтору клієнт бачить «тишу» посеред анкети/запису,
    хоча його попередня відповідь вже збережена в БД.
    """
    for attempt in range(1, attempts + 1):
        try:
            return await func(*args, **kwargs)
        except NetworkError as e:
            if attempt == attempts:
                raise
            logger.warning(
                f"⚠️ {getattr(func, '__qualname__', func)} не вдався "
                f"(спроба {attempt}/{attempts}): {e}. Повторюю..."
            )
            await asyncio.sleep(delay)