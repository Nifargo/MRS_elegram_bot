"""Диспетчер запланованих сповіщень. Викликається cron-ендпоінтом.

Реальна відправка різних типів сповіщень (нагадування, оцінки, привітання)
додається по мірі реалізації відповідних фаз плану — тут лише вибірка
"що вже пора відправити" з таблиці notifications.
"""
import logging
from datetime import datetime, timezone

from db import client as db
from db.client import supabase
from services import notifications

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


def _handle_form_incomplete(notification: dict) -> str:
    """Сповістити адмінів, якщо клієнт так і не заповнив анкету. Повертає новий статус."""
    client = db.get_client_by_id(notification["client_id"])
    if client is None or client["registration_done"]:
        return "sent"  # анкету заповнили (або клієнта видалили) — слати нічого

    who = client.get("name") or f"tg_user_id {client['tg_user_id']}"
    phone = client.get("phone") or "телефон не вказано"
    text = f"📋 Клієнт {who} ({phone}) запустив бота, але не заповнив анкету."
    return "sent" if notifications.notify_admins(text) else "failed"


# Обробники по типу сповіщення. Решта типів додається у Фазі 4+.
_HANDLERS = {
    "form_incomplete": _handle_form_incomplete,
}


def run_due() -> int:
    """Перевірити і обробити всі прострочені сповіщення. Повертає їх кількість."""
    due = get_due_notifications()
    logger.info(f"🔔 Знайдено {len(due)} сповіщень для відправки")

    for notification in due:
        handler = _HANDLERS.get(notification["type"])
        if handler is None:
            logger.info(f"  -> notification id={notification['id']} type={notification['type']} (обробка ще не реалізована)")
            continue
        try:
            status = handler(notification)
        except Exception as e:
            logger.error(f"❌ Помилка обробки notification id={notification['id']}: {e}", exc_info=True)
            status = "failed"
        db.mark_notification(notification["id"], status)
        logger.info(f"  -> notification id={notification['id']} type={notification['type']} -> {status}")

    return len(due)