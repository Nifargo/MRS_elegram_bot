import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import nest_asyncio

from config import TELEGRAM_TOKEN, WELCOME_MESSAGE
from groq_client import get_response, clear_chat_history

# Дозволити вкладені event loops
nest_asyncio.apply()

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask додаток
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start."""
    user_id = update.effective_user.id
    clear_chat_history(user_id)
    await update.message.reply_text(WELCOME_MESSAGE)
    logger.info(f"✅ Надіслано привітання користувачу {user_id}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник текстових повідомлень."""
    user_id = update.effective_user.id
    user_message = update.message.text

    logger.info(f"📨 Повідомлення від {user_id}: {user_message}")

    try:
        # Показати "друкує..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        logger.info("⌨️ Показано 'друкує...'")

        # Отримати відповідь від Groq
        response = await get_response(user_id, user_message)
        logger.info(f"✅ Отримано відповідь від Groq ({len(response)} символів)")

        # Надіслати відповідь користувачу
        await update.message.reply_text(response)
        logger.info(f"✅ Відповідь надіслано користувачу {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Помилка в handle_message: {e}", exc_info=True)
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте ще раз.")


# Додати обробники
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# Ініціалізувати Application при старті модуля
async def _initialize_application():
    """Ініціалізація Application."""
    await application.initialize()
    logger.info("✅ Application ініціалізовано!")


# Виконати ініціалізацію
asyncio.run(_initialize_application())
logger.info("✅ Бот готовий до роботи!")


@app.route('/')
def index():
    """Головна сторінка - перевірка що бот працює."""
    return "🐾 Mr.Snoopy Grooming Bot is running!"


@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    """Обробник webhook від Telegram."""
    try:
        # Отримати дані від Telegram
        json_data = request.get_json(force=True)
        
        logger.info(f"📥 Отримано webhook: update_id={json_data.get('update_id')}")
        
        # Створити Update об'єкт
        update = Update.de_json(json_data, application.bot)
        
        # Обробити update (Application вже ініціалізований)
        asyncio.run(application.process_update(update))
        
        logger.info("✅ Webhook оброблено успішно")
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"❌ Помилка обробки webhook: {e}", exc_info=True)
        return 'Error', 500


if __name__ == '__main__':
    # Для локального тестування
    app.run(debug=True, port=5000)
