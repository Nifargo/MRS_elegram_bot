"""Диспетчер запланованих сповіщень. Викликається cron-ендпоінтом.

Реальна відправка різних типів сповіщень (нагадування, оцінки, привітання)
додається по мірі реалізації відповідних фаз плану — тут лише вибірка
"що вже пора відправити" з таблиці notifications.
"""
import logging
from datetime import datetime, timezone

from handlers.common import parse_iso_datetime
from db import client as db
from db.client import supabase
from services import notifications, vaccine_sync
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

VACCINE_SYNC_HOUR = 10  # Київ; після цієї години перший виклик /cron за добу запускає синхронізацію
VACCINE_SYNC_KEY = "vaccine_sync"


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


def _handle_reminder_2h(notification: dict, application=None) -> str:
    """Нагадати клієнту про візит за ~2.5 год до початку."""
    record = db.get_tracked_record(notification["altegio_record_id"])
    if record is None or record["status"] != "active":
        return "sent"  # запис скасовано/зник — тихо гасимо

    client = db.get_client_by_id(record["client_id"])
    if client is None:
        return "sent"

    pet = db.get_pet(record["pet_id"]) if record.get("pet_id") else None
    who = f"{pet['name']} 🐾" if pet else "вас"
    starts = parse_iso_datetime(record["starts_at"]).astimezone(KYIV_TZ)
    text = (
        f"⏰ Нагадуємо: сьогодні о {starts.strftime('%H:%M')} чекаємо {who}\n"
        f"✂️ {record.get('service_title') or '—'}\n"
        f"📍 {record.get('location_title') or '—'}"
    )
    return "sent" if notifications.send_telegram_message(client["tg_user_id"], text) else "failed"


def _handle_thanks_rating(notification: dict, application=None) -> str:
    """Подякувати клієнту через 45 хв після завершення візиту і запитати оцінку послуги."""
    record = db.get_tracked_record(notification["altegio_record_id"])
    if record is None or record["status"] != "active":
        return "sent"

    client = db.get_client_by_id(record["client_id"])
    if client is None:
        return "sent"

    record_id = record["altegio_record_id"]
    text = "💛 Дякуємо, що завітали до Mr.Snoopy Grooming!\n\nЯк оцініте якість послуги?"
    keyboard = {"inline_keyboard": [[
        {"text": "⭐" * n, "callback_data": f"rt_svc:{record_id}:{n}"} for n in range(1, 6)
    ]]}
    return "sent" if notifications.send_telegram_message(client["tg_user_id"], text, reply_markup=keyboard) else "failed"


# Обробники по типу сповіщення. Решта типів додається у Фазі 4+.
# "vaccine" (Фаза 10) тут немає — sync_vaccine_dates() шле нагадування напряму,
# без проміжного рядка в notifications (див. _run_daily_tasks нижче).
_HANDLERS = {
    "form_incomplete": _handle_form_incomplete,
    "booking_incomplete": _handle_booking_incomplete,
    "reminder_2h": _handle_reminder_2h,
    "thanks_rating": _handle_thanks_rating,
}


def _run_daily_tasks() -> None:
    """Задачі, що виконуються раз на добу (а не при кожному 10-хвилинному тику).

    Диспетчер розрізняє «щоденне» від «кожні 10 хв» через cron_state: перший
    виклик /cron після VACCINE_SYNC_HOUR (Київ), для якого ще не було запуску
    сьогодні, і виконує задачу. `cron_state` позначається виконаним лише при
    повному успіху — якщо стався збій (виняток або хоч один клієнт не
    оброблений), день НЕ фіксується, і задача повториться на наступному тику
    того ж дня, а не чекатиме до завтра.
    """
    now = datetime.now(KYIV_TZ)
    if now.hour < VACCINE_SYNC_HOUR:
        return
    today = now.date().isoformat()
    if db.get_cron_last_run(VACCINE_SYNC_KEY) == today:
        return
    try:
        success = vaccine_sync.sync_vaccine_dates()
    except Exception as e:
        logger.error(f"❌ Помилка щоденної синхронізації вакцинації: {e}", exc_info=True)
        success = False
    if success:
        db.set_cron_last_run(VACCINE_SYNC_KEY, today)


def run_due(application=None) -> int:
    """Перевірити і обробити всі прострочені сповіщення. Повертає їх кількість.

    `application` — жива Telegram Application (якщо доступна), потрібна лише
    обробникам, яким треба прибрати пам'ятний стан клієнта (напр. booking_incomplete).
    """
    _run_daily_tasks()
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