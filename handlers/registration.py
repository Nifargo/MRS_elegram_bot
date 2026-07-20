"""Анкета реєстрації: телефон → локація → ім'я → прив'язка до Altegio → улюбленці.

Стан діалогу живе в ConversationHandler (in-memory); чернетка поточного
улюбленця додатково зберігається в clients.draft_json, а ім'я/телефон і кожен
завершений улюбленець пишуться в БД одразу — рестарт сервера не втрачає
заповнене.
"""
import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import ALTEGIO_LOCATIONS, WELCOME_MESSAGE
from db import client as db
from groq_client import clear_chat_history
from handlers.common import normalize_phone, parse_date, parse_weight, with_retry
from handlers.menu import MAIN_MENU
from services import altegio, altegio_sync
from services.altegio import AltegioError
from services.notifications import notify_admins_async, schedule_form_incomplete

logger = logging.getLogger(__name__)

# Питання про вакцинацію в анкеті немає навмисно: дату вакцинації веде
# адміністратор у картці клієнта Altegio, окрема автоматизація перевіряє
# прострочення і сповіщає адміна.
(PHONE, LOCATION, NAME, PET_NAME, PET_BREED, PET_BIRTH, PET_WEIGHT, PET_ALLERGIES,
 PET_BEHAVIOR, PET_PHOTO, ADD_MORE) = range(11)

BTN_SHARE_PHONE = "📱 Поділитись номером"
BTN_ADD_MORE = "➕ Додати ще одного"
BTN_FINISH = "✅ Завершити"

PHONE_KB = ReplyKeyboardMarkup(
    [[KeyboardButton(BTN_SHARE_PHONE, request_contact=True)]],
    resize_keyboard=True,
)
LOCATION_KB = ReplyKeyboardMarkup(
    [[name] for name in ALTEGIO_LOCATIONS],
    resize_keyboard=True,
)
ADD_MORE_KB = ReplyKeyboardMarkup([[BTN_ADD_MORE], [BTN_FINISH]], resize_keyboard=True)


def _save_draft(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Зберегти чернетку поточного улюбленця в clients.draft_json."""
    client_id = context.user_data["client_id"]
    try:
        db.update_client(client_id, {"draft_json": context.user_data.get("pet") or None})
    except Exception as e:
        logger.warning(f"Не вдалося зберегти чернетку анкети (client_id={client_id}): {e}")


def _company_ids_preferred_first(client: dict) -> list[str]:
    """company_id всіх філій; обрана клієнтом — першою."""
    preferred = client.get("altegio_company_id")
    company_ids = [cid for cid in ALTEGIO_LOCATIONS.values() if cid]
    if preferred in company_ids:
        company_ids.remove(preferred)
        company_ids.insert(0, preferred)
    return company_ids


def _search_altegio_client(client: dict) -> tuple[dict | None, bool]:
    """Пошук клієнта по телефону в усіх філіях (обрана — першою).

    Повертає (оновлений client або None, чи пошук пройшов без помилок).
    Знайденого одразу прив'язуємо; якщо в Altegio є ім'я, а у нас ще нема —
    забираємо його (салони працюють давно, більшість клієнтів уже в базі).
    """
    phone = client["phone"]
    company_ids = _company_ids_preferred_first(client)
    if not company_ids:
        logger.error("ALTEGIO_LOCATIONS порожній — нікуди прив'язувати клієнта")
        return None, False

    try:
        for company_id in company_ids:
            found = altegio.find_client_by_phone(company_id, phone.lstrip("+"))
            if found:
                logger.info(f"Клієнт {phone} знайдений в Altegio (company {company_id}), id={found['id']}")
                updates = {
                    "altegio_client_id": found["id"],
                    "altegio_company_id": company_id,
                }
                if not client.get("name") and found.get("name"):
                    updates["name"] = found["name"]
                return db.update_client(client["id"], updates), True
        return None, True
    except AltegioError as e:
        logger.error(f"Помилка пошуку клієнта {phone} в Altegio: {e}")
        return None, False


def _ensure_altegio_link(client: dict) -> dict:
    """Гарантувати прив'язку до Altegio: вже є → нічого; пошук → знайдено → прив'язати;
    не знайдено → створити в обраній філії.

    Створюємо ТІЛЬКИ якщо пошук завершився без помилок — інакше ризикуємо
    надублювати клієнтів з існуючої бази салону. Помилки не блокують анкету.
    """
    if client.get("altegio_client_id"):
        return client

    found, search_ok = _search_altegio_client(client)
    if found:
        return found
    if not search_ok:
        return client

    company_id = _company_ids_preferred_first(client)[0]
    try:
        created = altegio.create_client(company_id, client.get("name") or "", client["phone"].lstrip("+"))
        logger.info(f"Клієнт {client['phone']} створений в Altegio (company {company_id}), id={created['id']}")
        return db.update_client(client["id"], {
            "altegio_client_id": created["id"],
            "altegio_company_id": company_id,
        })
    except AltegioError as e:
        logger.error(f"Не вдалося створити клієнта {client['phone']} в Altegio: {e}")
        return client


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/start: зареєстрованим — меню, новим — анкета (телефон → локація → ім'я → улюбленці)."""
    user = update.effective_user
    clear_chat_history(user.id)

    client = db.get_client_by_tg_id(user.id)
    if client is None:
        client = db.create_client_record(user.id)
        try:
            schedule_form_incomplete(client["id"])
        except Exception as e:
            logger.warning(f"Не вдалося запланувати form_incomplete (client_id={client['id']}): {e}")
        logger.info(f"🆕 Новий клієнт tg_user_id={user.id}, id={client['id']}")

        username = f" (@{user.username})" if user.username else ""
        await notify_admins_async(
            context.bot,
            f"🆕 Новий користувач запустив бота: {user.full_name}{username}",
        )

    if client["registration_done"]:
        await with_retry(update.message.reply_text, WELCOME_MESSAGE, reply_markup=MAIN_MENU)
        return ConversationHandler.END

    context.user_data["client_id"] = client["id"]
    context.user_data["pet"] = {}

    await with_retry(update.message.reply_text,
        "Вітаю в Mr.Snoopy Grooming! 🐾\n"
        "Давайте знайомитись — це займе пару хвилин, і я зможу записувати "
        "ваших улюбленців на грумінг."
    )

    # Продовжуємо з того кроку, якого ще бракує (рестарт не втрачає прогрес)
    if not client.get("phone"):
        await with_retry(update.message.reply_text,
            "Поділіться номером телефону — за ним ми знайдемо вас у базі салону.",
            reply_markup=PHONE_KB,
        )
        return PHONE
    if not client.get("altegio_company_id"):
        return await _ask_location(update)
    if not client.get("name"):
        await with_retry(update.message.reply_text, "Як вас звати?", reply_markup=ReplyKeyboardRemove())
        return NAME
    _ensure_altegio_link(client)  # раптом минулого разу Altegio був недоступний

    existing_pets = db.get_pets_by_client(client["id"])
    if existing_pets:
        names = ", ".join(p["name"] for p in existing_pets)
        await with_retry(update.message.reply_text,
            f"Продовжимо анкету 🐶 Улюбленці, яких ви вже додали: {names}.\nДодати ще одного?",
            reply_markup=ADD_MORE_KB,
        )
        return ADD_MORE

    await with_retry(update.message.reply_text,
        "Продовжимо анкету 🐶 Як звати вашого улюбленця?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PET_NAME


async def add_pet_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback «➕ Додати улюбленця» зі списку улюбленців (клієнт вже зареєстрований)."""
    query = update.callback_query
    await query.answer()

    client = db.get_client_by_tg_id(update.effective_user.id)
    if client is None or not client["registration_done"]:
        await with_retry(query.message.reply_text, "Спочатку заповнимо коротку анкету — надішліть /start 🐾")
        return ConversationHandler.END

    context.user_data["client_id"] = client["id"]
    context.user_data["pet"] = {}
    context.user_data["adding_extra_pet"] = True

    await with_retry(query.message.reply_text, "Як звати улюбленця?", reply_markup=ReplyKeyboardRemove())
    return PET_NAME


async def got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.contact.phone_number if update.message.contact else update.message.text
    phone = normalize_phone(raw)
    if phone is None:
        await with_retry(update.message.reply_text,
            "Не розпізнав номер 😔 Надішліть у форматі +380XXXXXXXXX або "
            "натисніть кнопку нижче.",
            reply_markup=PHONE_KB,
        )
        return PHONE

    db.update_client(context.user_data["client_id"], {"phone": phone})
    return await _ask_location(update)


async def _ask_location(update: Update) -> int:
    await with_retry(update.message.reply_text,
        "В якій локації вам зручніше обслуговуватись? 📍",
        reply_markup=LOCATION_KB,
    )
    return LOCATION


async def got_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    location_name = update.message.text.strip()
    company_id = ALTEGIO_LOCATIONS.get(location_name)
    if not company_id:
        await with_retry(update.message.reply_text,
            "Оберіть локацію кнопкою нижче 🙂", reply_markup=LOCATION_KB
        )
        return LOCATION

    client = db.update_client(context.user_data["client_id"], {"altegio_company_id": company_id})

    # Салони працюють давно — спершу шукаємо клієнта в існуючій базі Altegio.
    found, _ = _search_altegio_client(client)
    if found and found.get("name"):
        await with_retry(update.message.reply_text,
            f"Знайшов вас у базі салону — {found['name']}, раді бачити знову! 💛\n"
            "Про вас ми вже знаємо, а от про ваших улюбленців — ще ні.\n"
            "Розкажіть про них: як звати вашого улюбленця?",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PET_NAME

    if found:
        await with_retry(update.message.reply_text,
            "Знайшов вас у базі салону 💛 Як вас звати?",
            reply_markup=ReplyKeyboardRemove(),
        )
        return NAME

    await with_retry(update.message.reply_text,
        f"Чудово, {location_name} 📍 Як вас звати?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if not name:
        await with_retry(update.message.reply_text, "Напишіть, будь ласка, ваше ім'я.")
        return NAME

    client = db.update_client(context.user_data["client_id"], {"name": name})
    _ensure_altegio_link(client)

    await with_retry(update.message.reply_text,
        f"Приємно познайомитись, {name}! Тепер розкажіть про вашого улюбленця.\n"
        "Як його звати?",
    )
    return PET_NAME


async def got_pet_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if not name:
        await with_retry(update.message.reply_text, "Напишіть, будь ласка, ім'я улюбленця.")
        return PET_NAME
    context.user_data["pet"] = {"name": name}
    _save_draft(context)
    await with_retry(update.message.reply_text, "Яка порода?", reply_markup=ReplyKeyboardRemove())
    return PET_BREED


async def got_pet_breed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    breed = update.message.text.strip()
    if not breed:
        await with_retry(update.message.reply_text, "Напишіть, будь ласка, породу.")
        return PET_BREED
    context.user_data["pet"]["breed"] = breed
    _save_draft(context)
    await with_retry(update.message.reply_text, "Дата народження? (ДД.ММ.РРРР, напр. 15.03.2022)")
    return PET_BIRTH


async def got_pet_birth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    birth = parse_date(update.message.text)
    if birth is None:
        await with_retry(update.message.reply_text,
            "Не розпізнав дату 😔 Формат: ДД.ММ.РРРР (напр. 15.03.2022), "
            "і дата не може бути в майбутньому."
        )
        return PET_BIRTH
    context.user_data["pet"]["birth_date"] = birth.isoformat()
    _save_draft(context)
    await with_retry(update.message.reply_text, "Вага в кг? (напр. 4.5)")
    return PET_WEIGHT


async def got_pet_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    weight = parse_weight(update.message.text)
    if weight is None:
        await with_retry(update.message.reply_text, "Не розпізнав вагу 😔 Напишіть число в кг, напр. 4.5")
        return PET_WEIGHT
    context.user_data["pet"]["weight"] = weight
    _save_draft(context)
    await with_retry(update.message.reply_text, "Чи є алергії? Якщо немає — напишіть «немає».")
    return PET_ALLERGIES


async def got_pet_allergies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    allergies = update.message.text.strip()
    if not allergies:
        await with_retry(update.message.reply_text, "Напишіть, будь ласка, чи є алергії (або «немає»).")
        return PET_ALLERGIES
    context.user_data["pet"]["allergies"] = allergies
    _save_draft(context)
    await with_retry(update.message.reply_text,
        "Особливості поведінки? (боїться фена, не любить чужих тощо; якщо немає — напишіть «немає»)"
    )
    return PET_BEHAVIOR


async def got_pet_behavior(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    behavior = update.message.text.strip()
    if not behavior:
        await with_retry(update.message.reply_text, "Напишіть, будь ласка, особливості поведінки (або «немає»).")
        return PET_BEHAVIOR
    context.user_data["pet"]["behavior_notes"] = behavior
    _save_draft(context)
    return await _ask_pet_photo(update)


async def _ask_pet_photo(update: Update) -> int:
    await with_retry(update.message.reply_text, "І останнє — фото улюбленця для картки 📸")
    return PET_PHOTO


async def got_pet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["pet"]["photo_file_id"] = update.message.photo[-1].file_id
    return await _finish_pet(update, context)


async def invalid_pet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await with_retry(update.message.reply_text, "Будь ласка, надішліть фото улюбленця 📸")
    return PET_PHOTO


async def _finish_pet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Зберегти улюбленця в БД, синхронізувати в Altegio, запитати про наступного."""
    client_id = context.user_data["client_id"]
    pet = context.user_data["pet"]

    db.create_pet(client_id, pet)
    context.user_data["pet"] = {}
    db.update_client(client_id, {"draft_json": None})

    client = db.get_client_by_id(client_id)
    if client:
        altegio_sync.sync_pets_comment(client)

    await with_retry(update.message.reply_text,
        f"🎉 {pet['name']} у списку ваших улюбленців!\nДодати ще одного?",
        reply_markup=ADD_MORE_KB,
    )
    return ADD_MORE


async def got_add_more(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == BTN_ADD_MORE:
        await with_retry(update.message.reply_text,
            "Як звати улюбленця?", reply_markup=ReplyKeyboardRemove()
        )
        return PET_NAME

    if update.message.text == BTN_FINISH:
        db.update_client(context.user_data["client_id"], {
            "registration_done": True,
            "draft_json": None,
        })
        if context.user_data.pop("adding_extra_pet", False):
            await with_retry(update.message.reply_text, "Улюбленця додано! 🐾", reply_markup=MAIN_MENU)
        else:
            await with_retry(update.message.reply_text,
                "Дякую, анкета заповнена! 💛\n"
                "Тепер можна записуватись на грумінг, дивитись картки улюбленців "
                "і питати мене про догляд.",
                reply_markup=MAIN_MENU,
            )
        return ConversationHandler.END

    await with_retry(update.message.reply_text, "Оберіть варіант кнопкою нижче 🙂", reply_markup=ADD_MORE_KB)
    return ADD_MORE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await with_retry(update.message.reply_text,
        "Добре, зупинив анкету. Продовжити можна будь-коли — просто надішліть /start.",
        reply_markup=MAIN_MENU,
    )
    return ConversationHandler.END


_TEXT = filters.TEXT & ~filters.COMMAND

conversation = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CallbackQueryHandler(add_pet_start, pattern=r"^pet_add$"),
    ],
    states={
        PHONE: [MessageHandler(filters.CONTACT | _TEXT, got_phone)],
        LOCATION: [MessageHandler(_TEXT, got_location)],
        NAME: [MessageHandler(_TEXT, got_name)],
        PET_NAME: [MessageHandler(_TEXT, got_pet_name)],
        PET_BREED: [MessageHandler(_TEXT, got_pet_breed)],
        PET_BIRTH: [MessageHandler(_TEXT, got_pet_birth)],
        PET_WEIGHT: [MessageHandler(_TEXT, got_pet_weight)],
        PET_ALLERGIES: [MessageHandler(_TEXT, got_pet_allergies)],
        PET_BEHAVIOR: [MessageHandler(_TEXT, got_pet_behavior)],
        PET_PHOTO: [
            MessageHandler(filters.PHOTO, got_pet_photo),
            MessageHandler(_TEXT, invalid_pet_photo),
        ],
        ADD_MORE: [MessageHandler(_TEXT, got_add_more)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    allow_reentry=True,
)