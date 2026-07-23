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


def _clear_booking_state(application, tg_user_id: int) -> None:
    """Прибрати «завислий» стан флоу запису з пам'яті бота (context.user_data).

    Без цього клієнт, що кинув запис і повернувся наступного дня, міг би
    натиснути стару inline-кнопку і потрапити в продовження вчорашнього флоу
    (застарілі дата/слоти) замість чіткого «сесію втрачено».
    """
    if application is None:
        return
    try:
        application.user_data.get(tg_user_id, {}).pop("booking", None)
    except Exception as e:
        logger.warning(f"Не вдалося очистити user_data booking для tg_user_id={tg_user_id}: {e}")


def _handle_form_incomplete(notification: dict, application=None) -> str:
    """Сповістити адмінів, якщо клієнт так і не заповнив анкету. Повертає новий статус."""
    client = db.get_client_by_id(notification["client_id"])
    if client is None or client["registration_done"]:
        return "sent"  # анкету заповнили (або клієнта видалили) — слати нічого

    who = client.get("name") or f"tg_user_id {client['tg_user_id']}"
    phone = client.get("phone") or "телефон не вказано"
    text = f"📋 Клієнт {who} ({phone}) запустив бота, але не заповнив анкету."
    return "sent" if notifications.notify_admins(text) else "failed"


def _handle_booking_incomplete(notification: dict, application=None) -> str:
    """Сповістити адмінів, якщо клієнт почав запис, але не завершив його того ж дня."""
    client = db.get_client_by_id(notification["client_id"])
    if client is None:
        return "sent"

    if db.has_tracked_record_since(client["id"], notification["created_at"]):
        return "sent"  # запис таки оформили після старту флоу — слати нічого

    _clear_booking_state(application, client["tg_user_id"])

    who = client.get("name") or f"tg_user_id {client['tg_user_id']}"
    phone = client.get("phone") or "телефон не вказано"
    text = (
        f"📵 Клієнт {who} ({phone}) почав запис на візит, але не завершив його.\n"
        "Можливо, виникла проблема — зателефонуйте, щоб дізнатись і допомогти."
    )
    return "sent" if notifications.notify_admins(text) else "failed"


# Обробники по типу сповіщення. Решта типів додається у Фазі 4+.
_HANDLERS = {
    "form_incomplete": _handle_form_incomplete,
    "booking_incomplete": _handle_booking_incomplete,
}


def run_due(application=None) -> int:
    """Перевірити і обробити всі прострочені сповіщення. Повертає їх кількість.

    `application` — жива Telegram Application (якщо доступна), потрібна лише
    обробникам, яким треба прибрати пам'ятний стан клієнта (напр. booking_incomplete).
    """
    due = get_due_notifications()
    logger.info(f"🔔 Знайдено {len(due)} сповіщень для відправки")

    for notification in due:
        handler = _HANDLERS.get(notification["type"])
        if handler is None:
            logger.info(f"  -> notification id={notification['id']} type={notification['type']} (обробка ще не реалізована)")
            continue
        try:
            status = handler(notification, application)
        except Exception as e:
            logger.error(f"❌ Помилка обробки notification id={notification['id']}: {e}", exc_info=True)
            status = "failed"
        db.mark_notification(notification["id"], status)
        logger.info(f"  -> notification id={notification['id']} type={notification['type']} -> {status}")

    return len(due)