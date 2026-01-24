import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN, WELCOME_MESSAGE
from groq_client import get_response, clear_chat_history

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start."""
    user_id = update.effective_user.id
    clear_chat_history(user_id)  # Почати новий чат
    await update.message.reply_text(WELCOME_MESSAGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник текстових повідомлень."""
    user_id = update.effective_user.id
    user_message = update.message.text

    logger.info(f"Повідомлення від {user_id}: {user_message}")

    # Показати "друкує..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Отримати відповідь від Gemini
    response = await get_response(user_id, user_message)

    await update.message.reply_text(response)


def main():
    """Запуск бота."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додати обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запустити бота
    logger.info("Бот запущено...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()