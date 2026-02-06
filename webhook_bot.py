import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from threading import Thread
import time

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

# Глобальні змінні
application = None
loop = None


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
        # Отримати відповідь від Groq
        response = await get_response(user_id, user_message)
        logger.info(f"✅ Отримано відповідь від Groq ({len(response)} символів)")

        # Надіслати відповідь користувачу
        await update.message.reply_text(response)
        logger.info(f"✅ Відповідь надіслано користувачу {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Помилка в handle_message: {e}", exc_info=True)
        try:
            await update.message.reply_text("Вибачте, сталася помилка. Спробуйте ще раз.")
        except:
            pass


def run_async_loop():
    """Запустити event loop в окремому потоці."""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.info("🔄 Event loop запущено в окремому потоці")
    loop.run_forever()


async def initialize_application():
    """Ініціалізувати Telegram Application."""
    global application
    
    # Створити Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Додати обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Ініціалізувати
    await application.initialize()
    await application.start()
    
    logger.info("✅ Telegram Application ініціалізовано!")


# Запустити event loop в окремому потоці
thread = Thread(target=run_async_loop, daemon=True)
thread.start()

# Почекати поки loop створено
while loop is None:
    time.sleep(0.1)

# Ініціалізувати Application в event loop
future = asyncio.run_coroutine_threadsafe(initialize_application(), loop)
future.result()

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
        
        # Обробити update в глобальному event loop (НЕ чекаємо на завершення)
        asyncio.run_coroutine_threadsafe(
            application.process_update(update),
            loop
        )
        
        # Відразу повертаємо 200 (Telegram отримає відповідь швидко)
        logger.info("✅ Webhook прийнято")
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"❌ Помилка обробки webhook: {e}", exc_info=True)
        return 'Error', 500


if __name__ == '__main__':
    # Для локального тестування
    app.run(debug=True, port=5000)
