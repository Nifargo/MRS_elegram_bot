"""Керування вже існуючими записами: список, перенос, скасування, повтор.

На відміну від handlers/booking.py (створення нового запису), тут маємо справу
з уже існуючими tracked_records. Стан переносу живе у
context.user_data["reschedule"] (той самий підхід, що і context.user_data["booking"]
у booking.py / чернетка редагування в pets.py).

Callback data:
  mb_reschedule:<id>       — почати перенос запису (id — tracked_records.id)
  mb_resch_pg:<page>       — пагінація дат переносу
  mb_resch_date:<iso>      — обрати нову дату
  mb_resch_time:<HH:MM>    — обрати новий час
  mb_resch_confirm         — підтвердити перенос
  mb_resch_cancel          — скасувати флоу переносу
  mb_cancel:<id>           — запит підтвердження скасування запису
  mb_cancel_confirm:<id>   — підтвердити скасування
  mb_cancel_abort          — назад без дій
  mb_repeat                — повторити останній запис
"""
import logging
from datetime import datetime, timedelta, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import client as db
from handlers import booking
from handlers.common import format_date_label, parse_iso_datetime, to_kyiv_iso, with_retry
from services.notifications import KYIV_TZ
from handlers.menu import MAIN_MENU
from services import altegio
from services.altegio import AltegioError

logger = logging.getLogger(__name__)

PAGE_SIZE_DATE = 12
RESCHEDULE_WINDOW = timedelta(hours=24)

CANCEL_BUTTON = InlineKeyboardButton("❌ Скасувати", callback_data="mb_resch_cancel")


# --- Допоміжне ---

def _get_own_record(tg_user_id: int, record_id: int) -> dict | None:
    """Запис, ТІЛЬКИ якщо він належить цьому користувачу (захист від IDOR)."""
    client = db.get_client_by_tg_id(tg_user_id)
    if client is None:
        return None
    record = db.get_tracked_record_by_id(record_id)
    if record is None or record["client_id"] != client["id"]:
        return None
    return record


def _within_reschedule_window(record: dict) -> bool:
    starts_at = parse_iso_datetime(record["starts_at"])
    return starts_at - datetime.now(timezone.utc) > RESCHEDULE_WINDOW


def _format_record_card(record: dict) -> str:
    pet = db.get_pet(record["pet_id"]) if record.get("pet_id") else None
    # starts_at повертається з Supabase в UTC — показуємо клієнту за Києвом.
    starts_at = parse_iso_datetime(record["starts_at"]).astimezone(KYIV_TZ)
    lines = []
    if pet:
        lines.append(f"🐾 {pet['name']} · {record.get('service_title') or '—'}")
    else:
        lines.append(f"✂️ {record.get('service_title') or '—'}")
    lines.append(f"📍 {record.get('location_title') or '—'}")
    lines.append(f"📅 {starts_at.strftime('%d.%m.%Y')} о {starts_at.strftime('%H:%M')}")
    return "\n".join(lines)


# --- Список записів ---

async def show_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка меню «🗓 Мої записи»."""
    client = db.get_client_by_tg_id(update.effective_user.id)
    if client is None or not client["registration_done"]:
        await with_retry(update.message.reply_text, "Спочатку заповнимо коротку анкету — надішліть /start 🐾")
        return

    upcoming = db.get_upcoming_tracked_records(client["id"])
    for record in upcoming:
        text = _format_record_card(record)
        if _within_reschedule_window(record):
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔁 Перенести", callback_data=f"mb_reschedule:{record['id']}"),
                    InlineKeyboardButton("❌ Скасувати", callback_data=f"mb_cancel:{record['id']}"),
                ],
            ])
            await with_retry(update.message.reply_text, text, reply_markup=kb)
        else:
            await with_retry(update.message.reply_text,
                text + "\n\n⏱ Перенести/скасувати можна не пізніше ніж за 24 год до візиту — "
                       "зверніться до адміністратора через «🆘 Допомога»."
            )

    last_past = db.get_last_past_tracked_record(client["id"])
    if last_past:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Повторити останній запис", callback_data="mb_repeat")]])
        await with_retry(update.message.reply_text, "Хочете записатись знову?", reply_markup=kb)

    if not upcoming and not last_past:
        await with_retry(update.message.reply_text, "У вас поки немає записів. Натисніть «📅 Записатись» 🐾")


# --- Перенос ---

async def _ask_reschedule_date(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    r = context.user_data["reschedule"]
    try:
        dates = altegio.get_available_dates(r["company_id"], staff_id=0, service_ids=[r["service_id"]])
    except AltegioError as e:
        logger.error(f"Altegio дати {r['company_id']}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити вільні дати 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    if not dates:
        await with_retry(message.reply_text, "На жаль, немає вільних дат найближчим часом. Зверніться 🆘 до адміністратора.")
        return

    r["dates"] = dates
    await _show_reschedule_date_page(message, context, 0)


async def _show_reschedule_date_page(message, context: ContextTypes.DEFAULT_TYPE, page: int) -> None:
    r = context.user_data["reschedule"]
    dates = r.get("dates", [])
    start = page * PAGE_SIZE_DATE
    chunk = dates[start:start + PAGE_SIZE_DATE]
    if not chunk:
        await with_retry(message.reply_text, "Дат не знайдено 😔")
        return

    rows = [
        [InlineKeyboardButton(format_date_label(d), callback_data=f"mb_resch_date:{d}") for d in chunk[i:i + 3]]
        for i in range(0, len(chunk), 3)
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"mb_resch_pg:{page - 1}"))
    if start + PAGE_SIZE_DATE < len(dates):
        nav.append(InlineKeyboardButton("➡️ Далі", callback_data=f"mb_resch_pg:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([CANCEL_BUTTON])

    await with_retry(message.reply_text, "Оберіть нову дату 📅:", reply_markup=InlineKeyboardMarkup(rows))


async def _ask_reschedule_time(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    r = context.user_data["reschedule"]
    try:
        times = altegio.get_available_times(r["company_id"], 0, r["date"], service_ids=[r["service_id"]])
    except AltegioError as e:
        logger.error(f"Altegio час {r['company_id']} {r['date']}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити вільний час 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    time_strs = [t["time"] for t in times]
    if not time_strs:
        await with_retry(message.reply_text, "На цю дату вже немає вільного часу 😔 Оберіть іншу дату.")
        await _show_reschedule_date_page(message, context, 0)
        return

    rows = [
        [InlineKeyboardButton(t, callback_data=f"mb_resch_time:{t}") for t in time_strs[i:i + 4]]
        for i in range(0, len(time_strs), 4)
    ]
    rows.append([CANCEL_BUTTON])
    await with_retry(message.reply_text, "Оберіть новий час 🕐:", reply_markup=InlineKeyboardMarkup(rows))


async def _show_reschedule_confirm(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    r = context.user_data["reschedule"]
    d = datetime.fromisoformat(r["date"])
    text = f"Перенести запис на {d.strftime('%d.%m.%Y')} о {r['time']}?"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Підтвердити", callback_data="mb_resch_confirm")],
        [CANCEL_BUTTON],
    ])
    await with_retry(message.reply_text, text, reply_markup=kb)


async def _confirm_reschedule(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    r = context.user_data["reschedule"]
    company_id, service_id = r["company_id"], r["service_id"]
    date_str, time_str = r["date"], r["time"]

    try:
        slot = altegio.find_available_staff_for_slot(company_id, service_id, date_str, time_str)
    except AltegioError as e:
        logger.error(f"Altegio пошук майстра {company_id}: {e}")
        await with_retry(message.reply_text, "Сталася помилка при перевірці вільного часу 😔 Спробуйте ще раз або зверніться 🆘.")
        return

    if slot is None:
        await with_retry(message.reply_text, "На жаль, цей час щойно зайняли 😔 Оберіть інший час.")
        await _ask_reschedule_time(message, context)
        return
    staff_id, seance_length = slot

    client = db.get_client_by_id(r["client_id"])
    altegio_client_id = booking.resolve_altegio_client_id(client, company_id)
    if altegio_client_id is None:
        await with_retry(message.reply_text, "Не вдалося перенести запис 😔 Зверніться 🆘 до адміністратора.")
        return

    try:
        altegio.move_record(
            company_id, r["altegio_record_id"], staff_id, altegio_client_id, service_id,
            f"{date_str} {time_str}:00", seance_length,
        )
    except AltegioError as e:
        logger.error(f"Altegio перенос запису {r['altegio_record_id']}: {e}")
        await with_retry(message.reply_text, "Не вдалося перенести запис 😔 Спробуйте ще раз або зверніться 🆘.")
        return

    db.upsert_tracked_record({
        "altegio_record_id": r["altegio_record_id"],
        "starts_at": to_kyiv_iso(date_str, time_str),
        "status": "active",
    })

    d = datetime.fromisoformat(date_str)
    await with_retry(message.reply_text,
        f"✅ Перенесено на {d.strftime('%d.%m.%Y')} о {time_str}",
        reply_markup=MAIN_MENU,
    )
    context.user_data.pop("reschedule", None)


# --- Скасування ---

def _cancel_confirm_keyboard(record_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Так, скасувати", callback_data=f"mb_cancel_confirm:{record_id}")],
        [InlineKeyboardButton("◀️ Ні", callback_data="mb_cancel_abort")],
    ])


async def _do_cancel(message, record: dict, context: ContextTypes.DEFAULT_TYPE) -> None:
    company_id = record.get("company_id")
    if not company_id:
        await with_retry(message.reply_text, "Не вдалося визначити деталі цього запису 😔 Зверніться до адміністратора через «🆘 Допомога».")
        return

    try:
        altegio.cancel_record(company_id, record["altegio_record_id"])
    except AltegioError as e:
        logger.error(f"Altegio скасування запису {record['altegio_record_id']}: {e}")
        await with_retry(message.reply_text, "Не вдалося скасувати запис 😔 Спробуйте ще раз або зверніться 🆘.")
        return

    db.update_tracked_record_status(record["altegio_record_id"], "cancelled")
    await with_retry(message.reply_text, "❌ Запис скасовано.", reply_markup=MAIN_MENU)


# --- Повтор останнього запису ---

async def _repeat_last_booking(message, context: ContextTypes.DEFAULT_TYPE, client_id: int) -> None:
    last = db.get_last_past_tracked_record(client_id)
    if last is None or not last.get("company_id") or not last.get("altegio_service_id"):
        await with_retry(message.reply_text, "Не вдалося визначити деталі минулого запису 😔 Оберіть послугу заново через «📅 Записатись».")
        return

    pet = db.get_pet(last["pet_id"]) if last.get("pet_id") else None
    if pet is None:
        await with_retry(message.reply_text, "Улюбленця з цього запису не знайдено — оберіть послугу заново через «📅 Записатись».")
        return

    company_id = last["company_id"]
    try:
        services = altegio.get_services(company_id)
    except AltegioError as e:
        logger.error(f"Altegio послуги {company_id}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити послуги 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    service = next((s for s in services if s["id"] == last["altegio_service_id"]), None)
    if service is None:
        await with_retry(message.reply_text, "Цю послугу більше не пропонують — оберіть нову через «📅 Записатись».")
        return

    slim_service = {
        "id": service["id"],
        "title": service["title"],
        "price_min": service.get("price_min"),
        "price_max": service.get("price_max"),
    }
    await booking.start_from_pet_and_service(
        message, context, client_id=client_id, pet=pet, company_id=company_id, service=slim_service,
    )


# --- Диспетчер ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "mb_resch_cancel":
        context.user_data.pop("reschedule", None)
        await with_retry(query.message.reply_text, "Скасовано.", reply_markup=MAIN_MENU)
        return

    if data == "mb_cancel_abort":
        await with_retry(query.message.reply_text, "Гаразд, запис лишається без змін.")
        return

    if data == "mb_repeat":
        client = db.get_client_by_tg_id(update.effective_user.id)
        if client is None:
            await with_retry(query.message.reply_text, "Спочатку заповнимо коротку анкету — надішліть /start 🐾")
            return
        await _repeat_last_booking(query.message, context, client["id"])
        return

    action, _, rest = data.partition(":")

    if action == "mb_reschedule":
        record = _get_own_record(update.effective_user.id, int(rest))
        if record is None:
            await with_retry(query.message.reply_text, "Не знайшов цей запис 😔")
            return
        if not record.get("company_id") or not record.get("altegio_service_id"):
            await with_retry(query.message.reply_text, "Не вдалося визначити деталі цього запису для переносу 😔 Зверніться до адміністратора через «🆘 Допомога».")
            return
        if not _within_reschedule_window(record):
            await with_retry(query.message.reply_text, "Перенести можна не пізніше ніж за 24 год до візиту — зверніться до адміністратора через «🆘 Допомога».")
            return
        context.user_data["reschedule"] = {
            "tracked_id": record["id"],
            "altegio_record_id": record["altegio_record_id"],
            "company_id": record["company_id"],
            "service_id": record["altegio_service_id"],
            "client_id": record["client_id"],
        }
        await _ask_reschedule_date(query.message, context)
        return

    if action == "mb_resch_pg":
        if "reschedule" not in context.user_data:
            await with_retry(query.message.reply_text, "Сесію переносу втрачено — почніть спочатку.")
            return
        await _show_reschedule_date_page(query.message, context, int(rest))
        return

    if action == "mb_resch_date":
        if "reschedule" not in context.user_data:
            await with_retry(query.message.reply_text, "Сесію переносу втрачено — почніть спочатку.")
            return
        context.user_data["reschedule"]["date"] = rest
        await _ask_reschedule_time(query.message, context)
        return

    if action == "mb_resch_time":
        if "reschedule" not in context.user_data:
            await with_retry(query.message.reply_text, "Сесію переносу втрачено — почніть спочатку.")
            return
        context.user_data["reschedule"]["time"] = rest
        await _show_reschedule_confirm(query.message, context)
        return

    if action == "mb_resch_confirm":
        if "reschedule" not in context.user_data:
            await with_retry(query.message.reply_text, "Сесію переносу втрачено — почніть спочатку.")
            return
        await _confirm_reschedule(query.message, context)
        return

    if action == "mb_cancel":
        record = _get_own_record(update.effective_user.id, int(rest))
        if record is None:
            await with_retry(query.message.reply_text, "Не знайшов цей запис 😔")
            return
        if not _within_reschedule_window(record):
            await with_retry(query.message.reply_text, "Скасувати можна не пізніше ніж за 24 год до візиту — зверніться до адміністратора через «🆘 Допомога».")
            return
        await with_retry(query.message.reply_text,
            f"Точно скасувати запис?\n\n{_format_record_card(record)}",
            reply_markup=_cancel_confirm_keyboard(record["id"]),
        )
        return

    if action == "mb_cancel_confirm":
        record = _get_own_record(update.effective_user.id, int(rest))
        if record is None:
            await with_retry(query.message.reply_text, "Не знайшов цей запис 😔")
            return
        if not _within_reschedule_window(record):
            await with_retry(query.message.reply_text, "Скасувати можна не пізніше ніж за 24 год до візиту — зверніться до адміністратора через «🆘 Допомога».")
            return
        await _do_cancel(query.message, record, context)
        return
