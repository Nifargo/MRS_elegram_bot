"""Диспетчер запланованих сповіщень. Викликається cron-ендпоінтом.

Реальна відправка різних типів сповіщень (нагадування, оцінки, привітання)
додається по мірі реалізації відповідних фаз плану — тут лише вибірка
"що вже пора відправити" з таблиці notifications.
"""
import logging
from datetime import datetime, timezone

from db.client import supabase

logger = logging.getLogger(__name__)


def get_due_notifications() -> list[dict]:
    """Сповіщення, які вже пора відправити (status=pending, send_after <= зараз)."""
    now = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("notifications")
        .select("*")
        .eq("status", "pending")
        .lte("send_after", now)
        .execute()
    )
    return result.data


def run_due() -> int:
    """Перевірити і обробити всі прострочені сповіщення. Повертає їх кількість."""
    due = get_due_notifications()
    logger.info(f"🔔 Знайдено {len(due)} сповіщень для відправки")

    for notification in due:
        # TODO: реальна відправка по типу (Фаза 4) — reminder_2h, thanks_rating, rebook_nudge, ...
        logger.info(f"  -> notification id={notification['id']} type={notification['type']} (обробка ще не реалізована)")

    return len(due)