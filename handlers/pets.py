"""Картки улюбленців: список → картка → редагування поле за полем.

Callback data:
  pet_list            — показати список улюбленців
  pet_show:<id>       — картка улюбленця
  pet_edit:<id>       — вибір поля для редагування
  pet_field:<id>:<f>  — редагувати поле f (вхід у ConversationHandler)
"""
import logging
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from db import client as db
from handlers.common import parse_date, parse_weight
from services import altegio_sync

logger = logging.getLogger(__name__)

EDIT_VALUE = 0

# поле -> (підпис, тип значення: text / date / weight / photo)
# Вакцинацію тут не ведемо: дата вакцинації живе в картці клієнта Altegio,
# окрема автоматизація стежить за простроченням.
EDITABLE_FIELDS = {
    "name": ("Ім'я", "text"),
    "breed": ("Порода", "text"),
    "birth_date": ("Дата народження", "date"),
    "weight": ("Вага", "weight"),
    "allergies": ("Алергії", "text"),
    "behavior_notes": ("Поведінка", "text"),
    "photo_file_id": ("Фото", "photo"),
}


def _get_own_pet(tg_user_id: int, pet_id: int) -> dict | None:
    """Картка улюбленця, ТІЛЬКИ якщо вона належить цьому користувачу.

    pet_id приходить у callback data, яку можна підробити — без цієї перевірки
    будь-хто міг би дивитись і редагувати чужі картки (IDOR).
    """
    client = db.get_client_by_tg_id(tg_user_id)
    if client is None:
        return None
    pet = db.get_pet(pet_id)
    if pet is None or pet["client_id"] != client["id"]:
        return None
    return pet


def _format_date(iso_date: str | None) -> str | None:
    if not iso_date:
        return None
    return date.fromisoformat(iso_date).strftime("%d.%m.%Y")


def _card_text(pet: dict) -> str:
    lines = [f"🐾 {pet['name']}"]
    if pet.get("breed"):
        lines.append(f"Порода: {pet['breed']}")
    if pet.get("birth_date"):
        lines.append(f"Дата народження: {_format_date(pet['birth_date'])}")
    if pet.get("weight"):
        lines.append(f"Вага: {pet['weight']} кг")
    if pet.get("allergies"):
        lines.append(f"Алергії: {pet['allergies']}")
    if pet.get("behavior_notes"):
        lines.append(f"Поведінка: {pet['behavior_notes']}")
    return "\n".join(lines)


def _list_keyboard(pets: list[dict]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"🐾 {pet['name']}", callback_data=f"pet_show:{pet['id']}")]
         for pet in pets]
    )


def _card_keyboard(pet_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Редагувати", callback_data=f"pet_edit:{pet_id}")],
        [InlineKeyboardButton("⬅️ До списку", callback_data="pet_list")],
    ])


def _edit_keyboard(pet_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data=f"pet_field:{pet_id}:{field}")]
        for field, (label, _) in EDITABLE_FIELDS.items()
    ]
    rows.append([InlineKeyboardButton("⬅️ Назад до картки", callback_data=f"pet_show:{pet_id}")])
    return InlineKeyboardMarkup(rows)


async def _send_card(message, pet: dict) -> None:
    """Надіслати картку улюбленця (з фото, якщо є)."""
    text = _card_text(pet)
    keyboard = _card_keyboard(pet["id"])
    if pet.get("photo_file_id"):
        await message.reply_photo(pet["photo_file_id"], caption=text, reply_markup=keyboard)
    else:
        await message.reply_text(text, reply_markup=keyboard)


async def show_pets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка меню «🐾 Мої улюбленці»."""
    client = db.get_client_by_tg_id(update.effective_user.id)
    if client is None or not client["registration_done"]:
        await update.message.reply_text(
            "Спочатку заповнимо коротку анкету — надішліть /start 🐾"
        )
        return

    pets = db.get_pets_by_client(client["id"])
    if not pets:
        await update.message.reply_text(
            "У вас поки немає доданих улюбленців. Надішліть /start, щоб додати."
        )
        return

    await update.message.reply_text("Ваші улюбленці:", reply_markup=_list_keyboard(pets))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка pet_list / pet_show / pet_edit."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "pet_list":
        client = db.get_client_by_tg_id(update.effective_user.id)
        pets = db.get_pets_by_client(client["id"]) if client else []
        if not pets:
            await query.message.reply_text("У вас поки немає доданих улюбленців.")
            return
        await query.message.reply_text("Ваші улюбленці:", reply_markup=_list_keyboard(pets))
        return

    action, pet_id = data.split(":", 1)
    pet = _get_own_pet(update.effective_user.id, int(pet_id))
    if pet is None:
        await query.message.reply_text("Не знайшов цю картку 😔")
        return

    if action == "pet_show":
        await _send_card(query.message, pet)
    elif action == "pet_edit":
        await query.message.reply_text(
            f"Що змінити у картці «{pet['name']}»?",
            reply_markup=_edit_keyboard(pet["id"]),
        )


# --- Редагування поля (ConversationHandler) ---

async def edit_field_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    _, pet_id, field = query.data.split(":", 2)
    pet = _get_own_pet(update.effective_user.id, int(pet_id))
    if pet is None or field not in EDITABLE_FIELDS:
        await query.message.reply_text("Не знайшов цю картку 😔")
        return ConversationHandler.END

    context.user_data["edit_pet_id"] = pet["id"]
    context.user_data["edit_field"] = field

    label, value_type = EDITABLE_FIELDS[field]
    prompts = {
        "text": f"Введіть нове значення поля «{label}»:",
        "date": f"Введіть нову дату поля «{label}» (ДД.ММ.РРРР):",
        "weight": "Введіть нову вагу в кг (напр. 4.5):",
        "photo": "Надішліть нове фото улюбленця 📸",
    }
    await query.message.reply_text(prompts[value_type] + "\n(або /cancel щоб скасувати)")
    return EDIT_VALUE


async def edit_field_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pet_id = context.user_data.get("edit_pet_id")
    field = context.user_data.get("edit_field")
    if pet_id is None or field is None or field not in EDITABLE_FIELDS:
        return ConversationHandler.END

    # Повторна перевірка власності перед записом: user_data могла застаріти
    if _get_own_pet(update.effective_user.id, pet_id) is None:
        context.user_data.pop("edit_pet_id", None)
        context.user_data.pop("edit_field", None)
        await update.message.reply_text("Не знайшов цю картку 😔")
        return ConversationHandler.END

    label, value_type = EDITABLE_FIELDS[field]

    if value_type == "photo":
        if not update.message.photo:
            await update.message.reply_text("Потрібне фото 📸 Надішліть зображення або /cancel.")
            return EDIT_VALUE
        value = update.message.photo[-1].file_id
    elif value_type == "date":
        parsed = parse_date(update.message.text)
        if parsed is None:
            await update.message.reply_text(
                "Не розпізнав дату 😔 Формат: ДД.ММ.РРРР, не в майбутньому. Або /cancel."
            )
            return EDIT_VALUE
        value = parsed.isoformat()
    elif value_type == "weight":
        parsed = parse_weight(update.message.text)
        if parsed is None:
            await update.message.reply_text(
                "Не розпізнав вагу 😔 Напишіть число в кг, напр. 4.5. Або /cancel."
            )
            return EDIT_VALUE
        value = parsed
    else:
        value = update.message.text.strip()
        if not value:
            await update.message.reply_text(f"Введіть значення поля «{label}» або /cancel.")
            return EDIT_VALUE

    pet = db.update_pet(pet_id, {field: value})

    client = db.get_client_by_id(pet["client_id"])
    if client:
        altegio_sync.sync_pets_comment(client)

    await update.message.reply_text(f"✅ Поле «{label}» оновлено!")
    await _send_card(update.message, pet)

    context.user_data.pop("edit_pet_id", None)
    context.user_data.pop("edit_field", None)
    return ConversationHandler.END


async def edit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("edit_pet_id", None)
    context.user_data.pop("edit_field", None)
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END


edit_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_field_start, pattern=r"^pet_field:\d+:\w+$")],
    states={
        EDIT_VALUE: [
            MessageHandler(filters.PHOTO, edit_field_value),
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_field_value),
        ],
    },
    fallbacks=[CommandHandler("cancel", edit_cancel)],
    allow_reentry=True,
)