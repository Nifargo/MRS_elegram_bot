"""Онлайн-запис на грумінг і перевірка вартості через Altegio.

Весь флоу — inline-кнопки + один диспетчер (`bk_...` callback data), без
ConversationHandler: жоден крок не потребує вільного тексту. Поточний стан
вибору живе у context.user_data["booking"] (той самий підхід, що і
handlers/pets.py для редагування карток).

Callback data:
  bk_pet:<id>         — обрати улюбленця
  bk_loc:<company_id> — обрати локацію
  bk_cat:<id>         — обрати категорію послуг
  bk_svc:<id>         — обрати послугу
  bk_all:<page>       — показати повний список послуг (з підказок по породі)
  bk_pg_svc:<page>    — пагінація повного списку послуг
  bk_switch_cat:<id>  — перемкнутись на інший рівень грумера (порода є тільки там)
  bk_contact_admin    — зв'язатись з адміністратором (номер салону)
  bk_toproceed        — з режиму «дізнатись вартість» перейти до запису
  bk_pg_date:<page>   — пагінація дат
  bk_date:<iso>       — обрати дату
  bk_time:<HH:MM>     — обрати час
  bk_confirm          — підтвердити запис
  bk_cancel           — скасувати флоу на будь-якому кроці
"""
import difflib
import logging
import re
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import ALTEGIO_LOCATIONS, HELP_PHONE
from db import client as db
from handlers.common import UA_WEEKDAYS, format_date_label, to_kyiv_iso, with_retry
from handlers.menu import MAIN_MENU
from services import altegio, notifications
from services.altegio import AltegioError

logger = logging.getLogger(__name__)

PAGE_SIZE_SVC = 8
PAGE_SIZE_DATE = 12

CANCEL_BUTTON = InlineKeyboardButton("❌ Скасувати", callback_data="bk_cancel")


# --- Форматування ---

def _format_price(service: dict) -> str:
    lo, hi = service.get("price_min"), service.get("price_max")
    if not lo:
        return "ціна за запитом"
    if hi and hi != lo:
        return f"{lo}–{hi} грн"
    return f"{lo} грн"


def _location_name(company_id: str) -> str:
    return next((name for name, cid in ALTEGIO_LOCATIONS.items() if cid == company_id), company_id)


def _slim_service(service: dict) -> dict:
    return {
        "id": service["id"],
        "title": service["title"],
        "price_min": service.get("price_min"),
        "price_max": service.get("price_max"),
    }


# --- Підказки по породі/вазі ---

def _weight_matches(title_lower: str, weight: float) -> bool:
    m = re.search(r"до\s*(\d+(?:[.,]\d+)?)\s*кг", title_lower)
    if m:
        return weight <= float(m.group(1).replace(",", "."))
    m = re.search(r"від\s*(\d+(?:[.,]\d+)?)\s*кг", title_lower)
    if m:
        return weight >= float(m.group(1).replace(",", "."))
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)\s*кг", title_lower)
    if m:
        lo, hi = float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))
        return lo <= weight <= hi
    return False


def _match_services_by_breed(breed: str, services: list[dict], weight: float | None) -> list[dict]:
    breed_lower = breed.lower().strip()
    if not breed_lower:
        return []
    words = [w for w in breed_lower.split() if len(w) >= 4]

    scored = []
    for service in services:
        title_lower = service["title"].lower()
        if breed_lower in title_lower or any(w in title_lower for w in words):
            score = 1.0
        else:
            score = difflib.SequenceMatcher(None, breed_lower, title_lower).ratio()
            if score < 0.4:
                continue
        if weight and _weight_matches(title_lower, weight):
            score += 0.5
        scored.append((score, service))

    scored.sort(key=lambda pair: -pair[0])
    return [service for _, service in scored[:6]]


def _category_type_key(title: str) -> str:
    """'Комплексний догляд (Топ грумер)' -> 'комплексний догляд' — для групування рівнів одного типу послуги."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", title).strip().lower()


def _sibling_categories(current_cat: dict, categories: list[dict]) -> list[dict]:
    key = _category_type_key(current_cat["title"])
    return [c for c in categories if c["id"] != current_cat["id"] and _category_type_key(c["title"]) == key]


def _generic_breed_services(cat_services: list[dict]) -> list[dict]:
    return [s for s in cat_services if s["title"].lower().startswith("інші породи")]


# --- Клавіатури ---

def _pet_keyboard(pets: list[dict]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"🐾 {pet['name']}", callback_data=f"bk_pet:{pet['id']}")] for pet in pets]
    rows.append([CANCEL_BUTTON])
    return InlineKeyboardMarkup(rows)


def _location_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(name, callback_data=f"bk_loc:{company_id}")]
        for name, company_id in ALTEGIO_LOCATIONS.items() if company_id
    ]
    rows.append([CANCEL_BUTTON])
    return InlineKeyboardMarkup(rows)


def _category_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(c["title"], callback_data=f"bk_cat:{c['id']}")] for c in categories]
    rows.append([CANCEL_BUTTON])
    return InlineKeyboardMarkup(rows)


def _service_row(service: dict) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(f"{service['title']} — {_format_price(service)}", callback_data=f"bk_svc:{service['id']}")]


# --- Вхід у флоу ---

async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str) -> None:
    client = db.get_client_by_tg_id(update.effective_user.id)
    if client is None or not client["registration_done"]:
        await with_retry(update.message.reply_text, "Спочатку заповнимо коротку анкету — надішліть /start 🐾")
        return

    pets = db.get_pets_by_client(client["id"])
    if not pets:
        await with_retry(update.message.reply_text,
            "Спершу додайте улюбленця: надішліть /start або скористайтесь кнопкою «🐾 Мої улюбленці»."
        )
        return

    if mode == "book":
        try:
            notifications.schedule_booking_incomplete(client["id"])
        except Exception as e:
            logger.warning(f"Не вдалося запланувати booking_incomplete (client_id={client['id']}): {e}")

    context.user_data["booking"] = {"mode": mode, "client_id": client["id"]}

    if len(pets) == 1:
        context.user_data["booking"]["pet"] = pets[0]
        await _ask_location(update.message, context)
    else:
        await with_retry(update.message.reply_text, "Кого записуємо? 🐾", reply_markup=_pet_keyboard(pets))


async def book_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка меню «📅 Записатись»."""
    await _start(update, context, "book")


async def price_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка меню «💰 Дізнатись вартість»."""
    await _start(update, context, "price")


async def start_from_pet_and_service(message, context: ContextTypes.DEFAULT_TYPE, *,
                                       client_id: int, pet: dict, company_id: str, service: dict) -> None:
    """Увійти у флоу запису одразу на кроці вибору дати (для «Повторити останній запис» з handlers/my_bookings.py)."""
    try:
        notifications.schedule_booking_incomplete(client_id)
    except Exception as e:
        logger.warning(f"Не вдалося запланувати booking_incomplete (client_id={client_id}): {e}")

    context.user_data["booking"] = {
        "mode": "book",
        "client_id": client_id,
        "pet": pet,
        "company_id": company_id,
        "service": service,
    }
    await _ask_date(message, context)


# --- Кроки флоу ---

async def _ask_location(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    await with_retry(message.reply_text, "В якій локації? 📍", reply_markup=_location_keyboard())


async def _show_location_card(message, company_id: str) -> None:
    try:
        company = altegio.get_company(company_id)
    except AltegioError as e:
        logger.error(f"Altegio company {company_id}: {e}")
        return

    lines = [f"📍 {company.get('title', _location_name(company_id))}"]
    if company.get("address"):
        lines.append(company["address"])
    if company.get("phone"):
        lines.append(f"☎️ {company['phone']}")
    await with_retry(message.reply_text, "\n".join(lines))

    lat, lon = company.get("coordinate_lat"), company.get("coordinate_lon")
    if lat and lon:
        await with_retry(message.reply_location, latitude=float(lat), longitude=float(lon))


async def _ask_category(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    b = context.user_data["booking"]
    try:
        categories = altegio.get_service_categories(b["company_id"])
    except AltegioError as e:
        logger.error(f"Altegio категорії {b['company_id']}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити послуги 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    if not categories:
        await with_retry(message.reply_text, "У цій локації поки немає послуг для онлайн-запису 😔")
        return

    b["categories"] = categories
    await with_retry(message.reply_text, "Яка послуга цікавить? 🐩", reply_markup=_category_keyboard(categories))


async def _ask_service(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    b = context.user_data["booking"]
    try:
        services = altegio.get_services(b["company_id"])
    except AltegioError as e:
        logger.error(f"Altegio послуги {b['company_id']}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити послуги 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    cat_services = sorted(
        (_slim_service(s) for s in services if s.get("category_id") == b["category_id"]),
        key=lambda s: s["title"],
    )
    if not cat_services:
        await with_retry(message.reply_text, "У цій категорії немає доступних послуг 😔")
        return

    b["services"] = cat_services

    pet = b["pet"]
    breed = (pet.get("breed") or "").strip()
    matches = _match_services_by_breed(breed, cat_services, pet.get("weight")) if breed else []

    if matches:
        rows = [_service_row(s) for s in matches]
        rows.append([InlineKeyboardButton(f"📋 Показати всі ({len(cat_services)})", callback_data="bk_all:0")])
        rows.append([CANCEL_BUTTON])
        await with_retry(message.reply_text,
            f"Схоже на «{pet['name']}» ({breed}):",
            reply_markup=InlineKeyboardMarkup(rows),
        )
        return

    if breed:
        categories = b.get("categories") or []
        current_cat = next((c for c in categories if c["id"] == b["category_id"]), None)
        siblings = _sibling_categories(current_cat, categories) if current_cat else []

        if siblings:
            level_hits = []
            for sib in siblings:
                sib_services = sorted(
                    (_slim_service(s) for s in services if s.get("category_id") == sib["id"]),
                    key=lambda s: s["title"],
                )
                if _match_services_by_breed(breed, sib_services, pet.get("weight")):
                    level_hits.append(sib)

            if level_hits:
                await _show_level_suggestion(message, pet, breed, level_hits)
                return

            generic = _generic_breed_services(cat_services)
            if generic:
                await _show_generic_fallback(message, pet, breed, generic, len(cat_services))
                return

    await _show_service_page(message, context, 0)


async def _show_level_suggestion(message, pet: dict, breed: str, level_hits: list[dict]) -> None:
    lines = [f"«{pet['name']}» ({breed}) немає серед послуг цього рівня.", "Ця порода є на рівні:"]
    rows = [
        [InlineKeyboardButton(f"➡️ {cat['title']}", callback_data=f"bk_switch_cat:{cat['id']}")]
        for cat in level_hits
    ]
    rows.append([InlineKeyboardButton("🆘 Допомога", callback_data="bk_contact_admin")])
    rows.append([CANCEL_BUTTON])
    await with_retry(message.reply_text, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def _show_generic_fallback(message, pet: dict, breed: str, generic_services: list[dict], total_count: int) -> None:
    text = f"«{pet['name']}» ({breed}) немає в нашому прайсі 😔 Оберіть за вагою:"
    rows = [_service_row(s) for s in generic_services]
    rows.append([InlineKeyboardButton(f"📋 Повний перелік послуг ({total_count})", callback_data="bk_all:0")])
    rows.append([InlineKeyboardButton("🆘 Зв'язатись з адміністратором", callback_data="bk_contact_admin")])
    rows.append([CANCEL_BUTTON])
    await with_retry(message.reply_text, text, reply_markup=InlineKeyboardMarkup(rows))


async def _show_service_page(message, context: ContextTypes.DEFAULT_TYPE, page: int) -> None:
    b = context.user_data["booking"]
    services = b.get("services", [])
    start = page * PAGE_SIZE_SVC
    chunk = services[start:start + PAGE_SIZE_SVC]
    if not chunk:
        await with_retry(message.reply_text, "Послуг не знайдено 😔")
        return

    rows = [_service_row(s) for s in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"bk_pg_svc:{page - 1}"))
    if start + PAGE_SIZE_SVC < len(services):
        nav.append(InlineKeyboardButton("➡️ Далі", callback_data=f"bk_pg_svc:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([CANCEL_BUTTON])

    total_pages = (len(services) - 1) // PAGE_SIZE_SVC + 1
    await with_retry(message.reply_text,
        f"Оберіть послугу (стор. {page + 1}/{total_pages}):",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def _select_service(message, context: ContextTypes.DEFAULT_TYPE, service_id: int) -> None:
    b = context.user_data["booking"]
    service = next((s for s in b.get("services", []) if s["id"] == service_id), None)
    if service is None:
        await with_retry(message.reply_text, "Не знайшов цю послугу 😔 Спробуйте ще раз.")
        return
    b["service"] = service

    if b["mode"] == "price":
        text = f"🐾 {b['pet']['name']} · {service['title']}\n💰 {_format_price(service)}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Записатись", callback_data="bk_toproceed")],
            [InlineKeyboardButton("❌ Закрити", callback_data="bk_cancel")],
        ])
        await with_retry(message.reply_text, text, reply_markup=kb)
        return

    await _ask_date(message, context)


async def _ask_date(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    b = context.user_data["booking"]
    try:
        dates = altegio.get_available_dates(b["company_id"], staff_id=0, service_ids=[b["service"]["id"]])
    except AltegioError as e:
        logger.error(f"Altegio дати {b['company_id']}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити вільні дати 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    if not dates:
        await with_retry(message.reply_text, "На жаль, немає вільних дат найближчим часом. Зверніться 🆘 до адміністратора.")
        return

    b["dates"] = dates
    await _show_date_page(message, context, 0)


async def _show_date_page(message, context: ContextTypes.DEFAULT_TYPE, page: int) -> None:
    b = context.user_data["booking"]
    dates = b.get("dates", [])
    start = page * PAGE_SIZE_DATE
    chunk = dates[start:start + PAGE_SIZE_DATE]
    if not chunk:
        await with_retry(message.reply_text, "Дат не знайдено 😔")
        return

    rows = [
        [InlineKeyboardButton(format_date_label(d), callback_data=f"bk_date:{d}") for d in chunk[i:i + 3]]
        for i in range(0, len(chunk), 3)
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"bk_pg_date:{page - 1}"))
    if start + PAGE_SIZE_DATE < len(dates):
        nav.append(InlineKeyboardButton("➡️ Далі", callback_data=f"bk_pg_date:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([CANCEL_BUTTON])

    await with_retry(message.reply_text, "Оберіть дату 📅:", reply_markup=InlineKeyboardMarkup(rows))


async def _ask_time(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    b = context.user_data["booking"]
    try:
        times = altegio.get_available_times(b["company_id"], 0, b["date"], service_ids=[b["service"]["id"]])
    except AltegioError as e:
        logger.error(f"Altegio час {b['company_id']} {b['date']}: {e}")
        await with_retry(message.reply_text, "Не вдалося завантажити вільний час 😔 Спробуйте пізніше або зверніться 🆘.")
        return

    time_strs = [t["time"] for t in times]
    if not time_strs:
        await with_retry(message.reply_text, "На цю дату вже немає вільного часу 😔 Оберіть іншу дату.")
        await _show_date_page(message, context, 0)
        return

    rows = [
        [InlineKeyboardButton(t, callback_data=f"bk_time:{t}") for t in time_strs[i:i + 4]]
        for i in range(0, len(time_strs), 4)
    ]
    rows.append([CANCEL_BUTTON])
    await with_retry(message.reply_text, "Оберіть час 🕐:", reply_markup=InlineKeyboardMarkup(rows))


async def _show_confirm(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    b = context.user_data["booking"]
    d = date.fromisoformat(b["date"])
    text = (
        "Підтвердіть запис:\n\n"
        f"🐾 {b['pet']['name']}\n"
        f"✂️ {b['service']['title']}\n"
        f"📍 {_location_name(b['company_id'])}\n"
        f"📅 {d.strftime('%d.%m.%Y')} ({UA_WEEKDAYS[d.weekday()]}) о {b['time']}\n"
        f"💰 {_format_price(b['service'])}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Підтвердити", callback_data="bk_confirm")],
        [CANCEL_BUTTON],
    ])
    await with_retry(message.reply_text, text, reply_markup=kb)


def resolve_altegio_client_id(client: dict, company_id: str) -> int | None:
    """Знайти або створити Altegio-клієнта для обраної локації.

    clients.altegio_company_id — «домашня» філія з реєстрації, її не чіпаємо:
    запис на іншу філію не повинен перезаписувати прив'язку клієнта.
    """
    if client.get("altegio_company_id") == company_id and client.get("altegio_client_id"):
        return client["altegio_client_id"]

    phone = (client.get("phone") or "").lstrip("+")
    if not phone:
        return None

    try:
        found = altegio.find_client_by_phone(company_id, phone)
        if found:
            return found["id"]
        created = altegio.create_client(company_id, client.get("name") or "", phone)
        return created["id"]
    except AltegioError as e:
        logger.error(f"Не вдалося прив'язати клієнта {client['id']} до філії {company_id}: {e}")
        return None


async def _confirm_booking(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    b = context.user_data["booking"]
    company_id = b["company_id"]
    service = b["service"]
    pet = b["pet"]
    date_str, time_str = b["date"], b["time"]

    try:
        slot = altegio.find_available_staff_for_slot(company_id, service["id"], date_str, time_str)
    except AltegioError as e:
        logger.error(f"Altegio пошук майстра {company_id}: {e}")
        await with_retry(message.reply_text, "Сталася помилка при перевірці вільного часу 😔 Спробуйте ще раз або зверніться 🆘.")
        return

    if slot is None:
        await with_retry(message.reply_text, "На жаль, цей час щойно зайняли 😔 Оберіть інший час.")
        await _ask_time(message, context)
        return
    staff_id, seance_length = slot

    client = db.get_client_by_id(b["client_id"])
    altegio_client_id = resolve_altegio_client_id(client, company_id)
    if altegio_client_id is None:
        await with_retry(message.reply_text, "Не вдалося оформити запис 😔 Зверніться 🆘 до адміністратора.")
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
        await with_retry(message.reply_text, "Не вдалося оформити запис 😔 Спробуйте ще раз або зверніться 🆘.")
        return

    location_name = _location_name(company_id)
    try:
        db.upsert_tracked_record({
            "altegio_record_id": record["id"],
            "client_id": b["client_id"],
            "pet_id": pet["id"],
            "starts_at": record.get("datetime") or to_kyiv_iso(date_str, time_str),
            "service_title": service["title"],
            "location_title": location_name,
            "status": "active",
            "company_id": company_id,
            "altegio_service_id": service["id"],
            "raw_json": record,
        })
    except Exception as e:
        logger.error(f"Не вдалося зберегти tracked_record {record.get('id')}: {e}")

    d = date.fromisoformat(date_str)
    await with_retry(message.reply_text,
        "🎉 Записано!\n"
        f"🐾 {pet['name']} · {service['title']}\n"
        f"📍 {location_name}\n"
        f"📅 {d.strftime('%d.%m.%Y')} о {time_str}",
        reply_markup=MAIN_MENU,
    )
    context.user_data.pop("booking", None)


# --- Диспетчер ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "bk_cancel":
        context.user_data.pop("booking", None)
        await with_retry(query.message.reply_text, "Скасовано.", reply_markup=MAIN_MENU)
        return

    b = context.user_data.get("booking")
    if b is None:
        await with_retry(query.message.reply_text,
            "Сесію запису втрачено — почніть спочатку кнопкою «📅 Записатись»."
        )
        return

    action, _, rest = data.partition(":")

    if action == "bk_pet":
        pet = db.get_pet(int(rest))
        if pet is None or pet["client_id"] != b["client_id"]:
            await with_retry(query.message.reply_text, "Не знайшов улюбленця 😔")
            return
        b["pet"] = pet
        await _ask_location(query.message, context)

    elif action == "bk_loc":
        b["company_id"] = rest
        await _show_location_card(query.message, rest)
        await _ask_category(query.message, context)

    elif action == "bk_cat":
        b["category_id"] = int(rest)
        await _ask_service(query.message, context)

    elif action in ("bk_all", "bk_pg_svc"):
        await _show_service_page(query.message, context, int(rest))

    elif action == "bk_switch_cat":
        b["category_id"] = int(rest)
        await _ask_service(query.message, context)

    elif action == "bk_svc":
        await _select_service(query.message, context, int(rest))

    elif action == "bk_contact_admin":
        await with_retry(query.message.reply_text, f"Зв'яжіться з нами по телефону: {HELP_PHONE}")

    elif action == "bk_toproceed":
        b["mode"] = "book"
        await _ask_date(query.message, context)

    elif action == "bk_pg_date":
        await _show_date_page(query.message, context, int(rest))

    elif action == "bk_date":
        b["date"] = rest
        await _ask_time(query.message, context)

    elif action == "bk_time":
        b["time"] = rest
        await _show_confirm(query.message, context)

    elif action == "bk_confirm":
        await _confirm_booking(query.message, context)
