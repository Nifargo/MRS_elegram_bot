import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from threading import Thread

from config import TELEGRAM_TOKEN, WELCOME_MESSAGE
from groq_client import get_response, clear_chat_history

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask додаток
app = Flask(__name__)

# Telegram Application
application = None
loop = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start."""
    user_id = update.effective_user.id
    clear_chat_history(user_id)
    await update.message.reply_text(WELCOME_MESSAGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник текстових повідомлень."""
    user_id = update.effective_user.id
    user_message = update.message.text

    logger.info(f"Повідомлення від {user_id}: {user_message}")

    # Показати "друкує..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Отримати відповідь від Groq
    response = await get_response(user_id, user_message)
    
    logger.info(f"✅ Отримано відповідь від Groq: {response[:50]}...")

    # Надіслати відповідь користувачу
    try:
        await update.message.reply_text(response)
        logger.info(f"✅ Відповідь надіслано користувачу {user_id}")
    except Exception as e:
        logger.error(f"❌ Помилка надсилання відповіді: {e}", exc_info=True)


def run_event_loop():
    """Запустити event loop в окремому потоці."""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()


def initialize_bot():
    """Ініціалізація бота при старті Flask."""
    global application
    
    # Запустити event loop в окремому потоці
    thread = Thread(target=run_event_loop, daemon=True)
    thread.start()
    
    # Почекати поки loop створено
    import time
    while loop is None:
        time.sleep(0.1)
    
    # Створити Application в event loop
    future = asyncio.run_coroutine_threadsafe(
        _create_application(),
        loop
    )
    application = future.result()
    
    logger.info("✅ Бот ініціалізовано успішно!")


async def _create_application():
    """Створити і ініціалізувати Application."""
    app_instance = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Додати обробники
    app_instance.add_handler(CommandHandler("start", start))
    app_instance.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Ініціалізувати
    await app_instance.initialize()
    
    return app_instance


# Ініціалізувати бота при імпорті модуля
initialize_bot()


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
        
        logger.info(f"Отримано webhook: {json_data}")
        
        # Створити Update об'єкт
        update = Update.de_json(json_data, application.bot)
        
        # Обробити update в глобальному event loop
        asyncio.run_coroutine_threadsafe(
            application.process_update(update),
            loop
        )
        
        return 'OK', 200
    except Exception as e:
        logger.error(f"❌ Помилка обробки webhook: {e}", exc_info=True)
        return 'Error', 500


if __name__ == '__main__':
    # Для локального тестування
    app.run(debug=True, port=5000)
