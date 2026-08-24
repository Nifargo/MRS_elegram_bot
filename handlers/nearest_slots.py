"""«🔥 Найближчі віконця» — запис до конкретного грумера, без переходу на Altegio-віджет.

Клієнту важливіше саме коли є вільне віконце, ніж вартість, тому порядок
кроків навмисно інший, ніж у booking.py: локація → майстер → час → (і лише
тоді) ціна.

Клавіатура майстрів фільтрується одразу після вибору локації: показуємо лише
тих, чий рівень (з тексту імені/категорії, як і в booking.py) реально має
послугу для породи улюбленця (`_breed_eligible_levels`). Порядок кроків після
цього: спочатку шукаємо й показуємо найближчі вільні віконця цього майстра
(ще без прив'язки до конкретної послуги — Altegio дає час без durations, якщо
не передати service_ids), і лише після того, як клієнт обрав час, показуємо
послуги для породи улюбленця з ціною — клієнт обирає сам, бот послугу не
вгадує. Якщо клієнт обирає «🎲 Будь-який майстер», рівень не обмежуємо — тут
збіг може бути неоднозначним (кілька рівнів одразу), тож завжди даємо клієнту
обрати послугу вручну зі списку.

Якщо порода нестандартна і жоден рівень з нею не працює — фільтрацію майстрів
не застосовуємо (показуємо всіх), а на кроці послуги одразу пропонуємо
підказки за вагою (generic_breed_services) + кнопку повного списку послуг, щоб
клієнт міг знайти свою породу (чи послугу для кота) вручну.

Найближчі вільні віконця збираються послідовним обходом get_available_dates →
get_available_times по датах (без service_ids — точна тривалість ще невідома),
поки не назбирається NEAREST_SLOTS_TARGET слотів або не скінчиться горизонт
NEAREST_SLOTS_HORIZON_DAYS. На кроці підтвердження (`_confirm`) слот
перевіряється живим запитом уже з конкретною послугою (service_ids) — це і
дає точну тривалість (seance_length) для create_record і захищає від того,
що слот зайняли, поки клієнт обирав послугу. Стан флоу — у
context.user_data["nearest"] (не персистентний, як і в booking.py/pets.py).

Callback data:
  ns_pet:<id>       — обрати улюбленця
  ns_loc:<company>  — обрати локацію
  ns_staff:<id>     — обрати майстра (0 = 🎲 будь-який майстер)
  ns_svc:<id>       — обрати послугу
  ns_all:<page>     — показати повний список послуг (з підказок по породі)
  ns_pg_svc:<page>  — пагінація повного списку послуг
  ns_slot:<index>   — обрати віконце зі списку найближчих
  ns_retry_staff    — повернутись до вибору іншого майстра (з екрана віконець)
  ns_confirm        — підтвердити запис
  ns_contact_admin  — зв'язатись з адміністратором (номер салону)
  ns_cancel         — скасувати флоу на будь-якому кроці
"""
import logging
import re
from datetime import date, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from config import ALTEGIO_LOCATIONS, HELP_PHONE
from db import client as db
from handlers import booking
from handlers.common import (
    UA_WEEKDAYS,
    format_date_label,
    hide_menu_button,
    kyiv_datetime,
    show_menu_button,
    with_retry,
)
from handlers.menu import MAIN_MENU
from services import altegio, notifications
from services.altegio import AltegioError

logger = logging.getLogger(__name__)

NEAREST_SLOTS_TARGET = 6
NEAREST_SLOTS_HORIZON_DAYS = 14

CANCEL_BUTTON = InlineKeyboardButton("❌ Скасувати", callback_data="ns_cancel")


# --- Рівень грумера: з тексту назви категорії/майстра ---

def _level_of_text(text: str) -> str:
    lower = text.lower()
    if "топ" in lower:
        return "топ"
    if "pro" in lower:
        return "pro"
    return "база"


def _category_level(category: dict) -> str:
    """'Комплексний догляд (Топ грумер)' -> 'топ' — рівень з тексту в дужках."""
    m = re.search(r"\(([^)]*)\)\s*$", category["title"])
    return _level_of_text(m.group(1)) if m else "база"


def _breed_eligible_levels(categories: list[dict], services: list[dict], breed: str, weight: float | None) -> set[str]:
    """Рівні грумера, у яких серед послуг є збіг по породі улюбленця."""
    if not breed:
        return set()
    levels = set()
    for lvl in ("база", "pro", "топ"):
        lvl_cat_ids = {c["id"] for c in categories if _category_level(c) == lvl}
        lvl_services = [booking.slim_service(s) for s in services if s.get("category_id") in lvl_cat_ids]
        if booking.match_services_by_breed(breed, lvl_services, weight):
            levels.add(lvl)
    return levels


# --- Клавіатури ---

def _pet_keyboard(pets: list[dict]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"🐾 {pet['name']}", callback_data=f"ns_pet:{pet['id']}")] for pet in pets]
    rows.append([CANCEL_BUTTON])
    return InlineKeyboardMarkup(rows)


def _location_keyboard() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(name, callback_data=f"ns_loc:{cid}")] for name, cid in ALTEGIO_LOCATIONS.items()]
    rows.append([CANCEL_BUTTON])
    return InlineKeyboardMarkup(rows)


def _staff_keyboard(staff_list: list[dict]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(s["name"], callback_data=f"ns_staff:{s['id']}")] for s in staff_list]
    rows.append([InlineKeyboardButton("🎲 Будь-який майстер", callback_data="ns_staff:0")])
    rows.append([CANCEL_BUTTON])
    return InlineKeyboardMarkup(rows)


def _service_row(service: dict) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(f"{service['title']} — {booking.format_price(service)}", callback_data=f"ns_svc:{service['id']}")]


def _slot_label(slot: dict) -> str:
    return f"{format_date_label(slot['date'])} о {slot['time']}"


# --- Вхід у флоу ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка меню «🔥 Найближчі віконця»."""
    result = await booking.registered_client_pets(update)
    if result is None:
        return
    client, pets = result
    await hide_menu_button(context.bot, update.effective_chat.id)

    try:
        notifications.schedule_booking_incomplete(client["id"])
    except Exception as e:
        logger.warning(f"Не вдалося запланувати booking_incomplete (client_id={client['id']}): {e}")

    await with_retry(update.message.reply_text, "🔥 Шукаємо найближчі вільні віконця...", reply_markup=ReplyKeyboardRemove())

    context.user_data["nearest"] = {"client_id": client["id"]}

    if len(pets) == 1:
        context.user_data["nearest"]["pet"] = pets[0]
        await _ask_location(update.message, context)
    else:
        await with_retry(update.message.reply_text, "Кого записуємо? 🐾", reply_markup=_pet_keyboard(pets))


# --- Кроки флоу ---

async def _ask_location(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    await with_retry(message.reply_text, "Яка локація вам підходить? 📍", reply_markup=_location_keyboard())


async def _ask_staff(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = context.user_data["nearest"]
    try:
        staff = altegio.get_staff(n["company_id"])
        categories = altegio.get_service_categories(n["company_id"])
        services = altegio.get_services(n["company_id"])
    except AltegioError as e:
        logger.error(f"Altegio майстри/послуги {n['company_id']}: {e}")
        await with_retry(message.reply_text,
            "Не вдалося завантажити майстрів 😔 Спробуйте пізніше або зверніться 🆘. "
            "Або запишіться самостійно за посиланням:",
            reply_markup=booking.booking_link_keyboard(),
        )
        return

    if not staff:
        await with_retry(message.reply_text, "У цій локації поки немає майстрів для запису 😔")
        return

    n["categories"] = categories
    n["all_services"] = services

    pet = n["pet"]
    breed = (pet.get("breed") or "").strip()
    eligible_levels = _breed_eligible_levels(categories, services, breed, pet.get("weight"))

    if eligible_levels:
        filtered_staff = [s for s in staff if _level_of_text(s["name"]) in eligible_levels]
        n["breed_generic"] = False
    else:
        # Нестандартна порода (чи ніде нема збігу) — жоден рівень не "правильніший",
        # показуємо всіх майстрів; послугу підбиратимемо за вагою на наступному кроці.
        filtered_staff = staff
        n["breed_generic"] = bool(breed)

    n["staff_list"] = filtered_staff
    await with_retry(message.reply_text, "Якого майстра оберете? 💇", reply_markup=_staff_keyboard(filtered_staff))


async def _ask_service(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = context.user_data["nearest"]
    categories = n.get("categories")
    services = n.get("all_services")
    if categories is None or services is None:
        try:
            categories = altegio.get_service_categories(n["company_id"])
            services = altegio.get_services(n["company_id"])
        except AltegioError as e:
            logger.error(f"Altegio послуги {n['company_id']}: {e}")
            await with_retry(message.reply_text,
                "Не вдалося завантажити послуги 😔 Спробуйте пізніше або зверніться 🆘. "
                "Або запишіться самостійно за посиланням:",
                reply_markup=booking.booking_link_keyboard(),
            )
            return

    level = n.get("level")
    candidate_cats = [c for c in categories if _category_level(c) == level] if level else categories
    cat_ids = {c["id"] for c in candidate_cats}
    candidate_services = sorted(
        (booking.slim_service(s) for s in services if s.get("category_id") in cat_ids),
        key=lambda s: s["title"],
    )
    if not candidate_services:
        await with_retry(message.reply_text, "У цього майстра немає доступних послуг для онлайн-запису 😔")
        return

    n["services"] = candidate_services

    pet = n["pet"]
    breed = (pet.get("breed") or "").strip()
    matches = booking.match_services_by_breed(breed, candidate_services, pet.get("weight")) if breed else []

    if matches:
        rows = [_service_row(s) for s in matches]
        rows.append([InlineKeyboardButton(f"📋 Показати всі ({len(candidate_services)})", callback_data="ns_all:0")])
        rows.append([CANCEL_BUTTON])
        await with_retry(message.reply_text,
            f"Схоже на «{pet['name']}» ({breed}):",
            reply_markup=InlineKeyboardMarkup(rows),
        )
        return

    if breed:
        generic = booking.generic_breed_services(candidate_services)
        if generic:
            await _show_generic_fallback(message, pet, breed, generic, len(candidate_services))
            return

    await _show_service_page(message, context, 0)


async def _show_generic_fallback(message, pet: dict, breed: str, generic_services: list[dict], total_count: int) -> None:
    text = f"«{pet['name']}» ({breed}) немає в нашому прайсі 😔 Оберіть за вагою:"
    rows = [_service_row(s) for s in generic_services]
    rows.append([InlineKeyboardButton(f"📋 Повний перелік послуг ({total_count})", callback_data="ns_all:0")])
    rows.append([InlineKeyboardButton("🆘 Зв'язатись з адміністратором", callback_data="ns_contact_admin")])
    rows.append([CANCEL_BUTTON])
    await with_retry(message.reply_text, text, reply_markup=InlineKeyboardMarkup(rows))


async def _show_service_page(message, context: ContextTypes.DEFAULT_TYPE, page: int) -> None:
    n = context.user_data["nearest"]
    services = n.get("services", [])
    start_i = page * booking.PAGE_SIZE_SVC
    chunk = services[start_i:start_i + booking.PAGE_SIZE_SVC]
    if not chunk:
        await with_retry(message.reply_text, "Послуг не знайдено 😔")
        return

    rows = [_service_row(s) for s in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"ns_pg_svc:{page - 1}"))
    if start_i + booking.PAGE_SIZE_SVC < len(services):
        nav.append(InlineKeyboardButton("➡️ Далі", callback_data=f"ns_pg_svc:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([CANCEL_BUTTON])

    total_pages = (len(services) - 1) // booking.PAGE_SIZE_SVC + 1
    await with_retry(message.reply_text,
        f"Оберіть послугу (стор. {page + 1}/{total_pages}):",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def _select_service(message, context: ContextTypes.DEFAULT_TYPE, service_id: int) -> None:
    n = context.user_data["nearest"]
    service = next((s for s in n.get("services", []) if s["id"] == service_id), None)
    if service is None:
        await with_retry(message.reply_text, "Не знайшов цю послугу 😔 Спробуйте ще раз.")
        return
    n["service"] = service
    await _show_confirm(message, context)


async def _search_nearest_slots(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Найближчі вільні віконця майстра без прив'язки до послуги (ще не обрана).

    Без service_ids Altegio віддає час для дефолтної тривалості — цього
    достатньо, щоб показати клієнту ГОДИНИ; точну тривалість перевіримо
    повторним запитом уже з конкретною послугою на кроці підтвердження (_confirm).
    """
    n = context.user_data["nearest"]
    company_id = n["company_id"]
    staff_id = n.get("staff_id") or 0

    try:
        dates = altegio.get_available_dates(company_id, staff_id=staff_id)
    except AltegioError as e:
        logger.error(f"Altegio дати {company_id}: {e}")
        await with_retry(message.reply_text,
            "Не вдалося завантажити вільні дати 😔 Спробуйте пізніше або зверніться 🆘. "
            "Або запишіться самостійно за посиланням:",
            reply_markup=booking.booking_link_keyboard(),
        )
        return

    if not dates:
        await with_retry(message.reply_text, "На жаль, немає вільних дат найближчим часом. Зверніться 🆘 до адміністратора.")
        return

    slots = []
    for d in dates[:NEAREST_SLOTS_HORIZON_DAYS]:
        try:
            times = altegio.get_available_times(company_id, staff_id, d)
        except AltegioError as e:
            logger.warning(f"Altegio час {company_id} {d}: {e}")
            continue
        for t in times:
            slots.append({"date": d, "time": t["time"]})
            if len(slots) >= NEAREST_SLOTS_TARGET:
                break
        if len(slots) >= NEAREST_SLOTS_TARGET:
            break

    if not slots:
        await with_retry(message.reply_text, "На жаль, немає вільного часу найближчим часом. Зверніться 🆘 до адміністратора.")
        return

    n["slots"] = slots
    await _show_slots(message, context)


async def _show_slots(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = context.user_data["nearest"]
    rows = [
        [InlineKeyboardButton(_slot_label(s), callback_data=f"ns_slot:{i}")]
        for i, s in enumerate(n["slots"])
    ]
    rows.append([InlineKeyboardButton("🔁 Обрати іншого майстра", callback_data="ns_retry_staff")])
    rows.append([CANCEL_BUTTON])
    await with_retry(message.reply_text, "Найближчі вільні віконця 🕐:", reply_markup=InlineKeyboardMarkup(rows))


async def _select_slot(message, context: ContextTypes.DEFAULT_TYPE, index: int) -> None:
    n = context.user_data["nearest"]
    slots = n.get("slots", [])
    if index < 0 or index >= len(slots):
        await with_retry(message.reply_text, "Не знайшов це віконце 😔 Спробуйте ще раз.")
        return
    slot = slots[index]
    n["date"] = slot["date"]
    n["time"] = slot["time"]
    await _ask_service(message, context)


async def _show_confirm(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = context.user_data["nearest"]
    d = date.fromisoformat(n["date"])
    staff_line = f"💇 {n['staff_display_name']}" if n.get("staff_display_name") else "💇 Будь-який майстер"
    text = (
        "Підтвердіть запис:\n\n"
        f"🐾 {n['pet']['name']}\n"
        f"✂️ {n['service']['title']}\n"
        f"{staff_line}\n"
        f"📍 {booking.location_name(n['company_id'])}\n"
        f"📅 {d.strftime('%d.%m.%Y')} ({UA_WEEKDAYS[d.weekday()]}) о {n['time']}\n"
        f"💰 {booking.format_price(n['service'])}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Підтвердити", callback_data="ns_confirm")],
        [CANCEL_BUTTON],
    ])
    await with_retry(message.reply_text, text, reply_markup=kb)


async def _confirm(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = context.user_data["nearest"]
    company_id = n["company_id"]
    service = n["service"]
    pet = n["pet"]
    date_str, time_str = n["date"], n["time"]

    if n.get("staff_id"):
        # Живий перепит: слот показувався клієнту зі списку, зібраного заздалегідь
        # (пошук по кількох датах), тож до підтвердження могло минути багато часу —
        # перевіряємо, що цей майстер усе ще вільний саме на цей час.
        try:
            times = altegio.get_available_times(company_id, n["staff_id"], date_str, service_ids=[service["id"]])
        except AltegioError as e:
            logger.error(f"Altegio час {company_id} {date_str}: {e}")
            await with_retry(message.reply_text,
                "Сталася помилка при перевірці вільного часу 😔 Спробуйте ще раз або зверніться 🆘. "
                "Або запишіться самостійно за посиланням:",
                reply_markup=booking.booking_link_keyboard(),
            )
            return
        slot_time = next((t for t in times if t["time"] == time_str), None)
        slot = (n["staff_id"], slot_time["seance_length"]) if slot_time else None
    else:
        try:
            slot = altegio.find_available_staff_for_slot(company_id, service["id"], date_str, time_str)
        except AltegioError as e:
            logger.error(f"Altegio пошук майстра {company_id}: {e}")
            await with_retry(message.reply_text,
                "Сталася помилка при перевірці вільного часу 😔 Спробуйте ще раз або зверніться 🆘. "
                "Або запишіться самостійно за посиланням:",
                reply_markup=booking.booking_link_keyboard(),
            )
            return

    if slot is None:
        await with_retry(message.reply_text, "На жаль, цей час щойно зайняли 😔 Спробуйте пошук ще раз кнопкою «🔥 Найближчі віконця».")
        context.user_data.pop("nearest", None)
        await show_menu_button(context.bot, message.chat_id)
        return
    staff_id, seance_length = slot

    client = db.get_client_by_id(n["client_id"])
    altegio_client_id = booking.resolve_altegio_client_id(client, company_id)
    if altegio_client_id is None:
        await with_retry(message.reply_text,
            "Не вдалося оформити запис 😔 Зверніться 🆘 до адміністратора. "
            "Або запишіться самостійно за посиланням:",
            reply_markup=booking.booking_link_keyboard(),
        )
        return

    comment_parts = [pet["name"]]
    if pet.get("breed"):
        comment_parts.append(pet["breed"])
    if pet.get("weight"):
        comment_parts.append(f"{pet['weight']} кг")
    if pet.get("allergies"):
        comment_parts.append(f"алергії: {pet['allergies']}")
    if pet.get("behavior_notes"):
        comment_parts.append(f"поведінка: {pet['behavior_notes']}")
    comment = " · ".join(comment_parts)

    try:
        record = altegio.create_record(
            company_id, altegio_client_id, staff_id, service["id"],
            f"{date_str} {time_str}:00", seance_length, comment=comment,
        )
    except AltegioError as e:
        logger.error(f"Не вдалося створити запис: {e}")
        await with_retry(message.reply_text,
            "Не вдалося оформити запис 😔 Спробуйте ще раз або зверніться 🆘. "
            "Або запишіться самостійно за посиланням:",
            reply_markup=booking.booking_link_keyboard(),
        )
        return

    loc_name = booking.location_name(company_id)
    starts_dt = kyiv_datetime(date_str, time_str)
    ends_dt = starts_dt + timedelta(seconds=seance_length)
    try:
        db.upsert_tracked_record({
            "altegio_record_id": record["id"],
            "client_id": n["client_id"],
            "pet_id": pet["id"],
            # Не `record["datetime"]`: Altegio віддає там offset +03:00 і в
            # зимовий сезон, коли Київ у +02:00 (див. services/altegio_webhook.py).
            "starts_at": starts_dt.isoformat(),
            "ends_at": ends_dt.isoformat(),
            "service_title": service["title"],
            "location_title": loc_name,
            "status": "active",
            "company_id": company_id,
            "altegio_service_id": service["id"],
            "staff_id": staff_id,
            "raw_json": record,
        })
        notifications.schedule_visit_notifications(n["client_id"], record["id"], starts_dt, ends_dt)
    except Exception as e:
        logger.error(f"Не вдалося зберегти tracked_record {record.get('id')}: {e}")

    d = date.fromisoformat(date_str)
    await with_retry(message.reply_text,
        "🎉 Записано!\n"
        f"🐾 {pet['name']} · {service['title']}\n"
        f"📍 {loc_name}\n"
        f"📅 {d.strftime('%d.%m.%Y')} о {time_str}",
        reply_markup=MAIN_MENU,
    )
    context.user_data.pop("nearest", None)
    await show_menu_button(context.bot, message.chat_id)


# --- Диспетчер ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await with_retry(query.answer)
    data = query.data

    if data == "ns_cancel":
        context.user_data.pop("nearest", None)
        await show_menu_button(context.bot, update.effective_chat.id)
        await with_retry(query.message.reply_text, "Скасовано.", reply_markup=MAIN_MENU)
        return

    n = context.user_data.get("nearest")
    if n is None:
        await show_menu_button(context.bot, update.effective_chat.id)
        await with_retry(query.message.reply_text,
            "Сесію втрачено — почніть спочатку кнопкою «🔥 Найближчі віконця».",
            reply_markup=MAIN_MENU,
        )
        return

    if data == "ns_contact_admin":
        await with_retry(query.message.reply_text, f"Зв'яжіться з нами по телефону: {HELP_PHONE}")
        return

    if data == "ns_confirm":
        await _confirm(query.message, context)
        return

    if data == "ns_retry_staff":
        await _ask_staff(query.message, context)
        return

    action, _, rest = data.partition(":")

    if action == "ns_pet":
        pet = db.get_pet(int(rest))
        if pet is None or pet["client_id"] != n["client_id"]:
            await with_retry(query.message.reply_text, "Не знайшов улюбленця 😔")
            return
        n["pet"] = pet
        await _ask_location(query.message, context)

    elif action == "ns_loc":
        n["company_id"] = rest
        await _ask_staff(query.message, context)

    elif action == "ns_staff":
        staff_id = int(rest)
        if staff_id:
            member = next((s for s in n.get("staff_list", []) if s["id"] == staff_id), None)
            n["staff_id"] = staff_id
            n["staff_display_name"] = member["name"] if member else None
            n["level"] = _level_of_text(n["staff_display_name"] or "")
        else:
            n["staff_id"] = None
            n["staff_display_name"] = None
            n["level"] = None
        await with_retry(query.message.reply_text, "🔎 Шукаю найближчі вільні віконця...")
        await _search_nearest_slots(query.message, context)

    elif action in ("ns_all", "ns_pg_svc"):
        await _show_service_page(query.message, context, int(rest))

    elif action == "ns_svc":
        await _select_service(query.message, context, int(rest))

    elif action == "ns_slot":
        await _select_slot(query.message, context, int(rest))
