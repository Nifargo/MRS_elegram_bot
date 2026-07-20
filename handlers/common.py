"""Спільні валідатори полів анкети та карток улюбленців."""
import asyncio
import logging
import re
from datetime import date, datetime

from telegram.error import NetworkError

logger = logging.getLogger(__name__)


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


async def with_retry(func, *args, attempts: int = 3, delay: float = 1.5, **kwargs):
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