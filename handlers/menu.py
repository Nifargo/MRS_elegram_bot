"""Головне меню бота."""
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

BTN_BOOK = "📅 Записатись"
BTN_PRICE = "💰 Дізнатись вартість"
BTN_MY_BOOKINGS = "🗓 Мої записи"
BTN_MY_PETS = "🐾 Мої улюбленці"
BTN_HISTORY = "✂️ Історія"
BTN_BONUSES = "🎁 Бонуси"
BTN_AI = "💬 Питання (AI)"
BTN_HELP = "🆘 Допомога"

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [BTN_BOOK, BTN_PRICE],
        [BTN_MY_BOOKINGS, BTN_MY_PETS],
        [BTN_HISTORY, BTN_BONUSES],
        [BTN_AI, BTN_HELP],
    ],
    resize_keyboard=True,
)

# Кнопки, чий функціонал ще не реалізовано (наступні фази плану).
# BTN_MY_PETS обробляється в handlers/pets.py (Фаза 1).
# BTN_BOOK/BTN_PRICE обробляються в handlers/booking.py (Фаза 2).
_PLACEHOLDER_BUTTONS = {BTN_MY_BOOKINGS, BTN_HISTORY, BTN_BONUSES, BTN_HELP}


def is_menu_button(text: str) -> bool:
    return text in _PLACEHOLDER_BUTTONS or text == BTN_AI


async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Обробити натискання кнопки меню. Повертає True, якщо повідомлення оброблено тут."""
    text = update.message.text

    if text == BTN_AI:
        await update.message.reply_text("Питайте — відповім про послуги, догляд і запис 🐾")
        return True

    if text in _PLACEHOLDER_BUTTONS:
        await update.message.reply_text("🚧 Ця функція ще в розробці, скоро буде доступна!")
        return True

    return False