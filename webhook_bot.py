import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import asyncio
from threading import Thread
import time

from config import TELEGRAM_TOKEN, CRON_SECRET
from handlers.setup import register_handlers
from services import scheduler

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
thread = None


def run_async_loop():
    """Запустити event loop в окремому потоці."""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.info("🔄 Event loop запущено в окремому потоці")
    try:
        loop.run_forever()
    except Exception as e:
        logger.error(f"❌ Event loop впав: {e}", exc_info=True)
    finally:
        loop = None
        logger.warning("⚠️ Event loop зупинено!")


async def initialize_application():
    """Ініціалізувати Telegram Application."""
    global application

    # Створити Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додати обробники (спільні з bot.py)
    register_handlers(application)

    # Ініціалізувати
    await application.initialize()
    await application.start()

    logger.info("✅ Telegram Application ініціалізовано!")


def _is_loop_alive():
    """Перевірити чи event loop живий і працює."""
    return (
        loop is not None
        and thread is not None
        and thread.is_alive()
        and loop.is_running()
    )


def ensure_initialized():
    """Переконатись що бот ініціалізований. Перезапускає якщо event loop помер."""
    global application, loop, thread

    if application is not None and _is_loop_alive():
        return True

    # Скинути стан якщо loop помер
    if loop is not None or application is not None:
        logger.warning("⚠️ Event loop помер! Перезапускаю...")
        application = None
        loop = None
        thread = None

    logger.info("🚀 Запуск ініціалізації бота...")

    # Запустити event loop в окремому потоці
    thread = Thread(target=run_async_loop, daemon=True)
    thread.start()

    # Почекати поки loop створено
    timeout = 10
    start_time = time.time()
    while loop is None and (time.time() - start_time) < timeout:
        time.sleep(0.1)

    if loop is None:
        logger.error("❌ Event loop не створився за 10 секунд!")
        return False

    logger.info("✅ Event loop створено!")

    # Ініціалізувати Application в event loop
    try:
        future = asyncio.run_coroutine_threadsafe(initialize_application(), loop)
        future.result(timeout=30)
        logger.info("✅ Бот готовий до роботи!")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації Application: {e}", exc_info=True)
        return False


@app.route('/')
def index():
    """Головна сторінка - перевірка що бот працює."""
    try:
        ensure_initialized()
        return "🐾 Mr.Snoopy Grooming Bot is running!"
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації: {e}", exc_info=True)
        return f"Error: {e}", 500


@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    """Обробник webhook від Telegram."""
    try:
        # Переконатись що бот ініціалізований (3 спроби)
        initialized = False
        for attempt in range(1, 4):
            if ensure_initialized():
                initialized = True
                break
            logger.warning(f"⚠️ Спроба ініціалізації {attempt}/3 не вдалась, чекаю 2с...")
            time.sleep(2)

        if not initialized:
            logger.error("❌ Бот не ініціалізований після 3 спроб, webhook відхилено")
            return 'Bot not initialized', 503

        # Отримати дані від Telegram
        json_data = request.get_json(force=True)

        logger.info(f"📥 Отримано webhook: update_id={json_data.get('update_id')}")

        # Створити Update об'єкт
        update = Update.de_json(json_data, application.bot)

        # Обробити update в event loop
        future = asyncio.run_coroutine_threadsafe(
            application.process_update(update),
            loop
        )

        # Почекати на результат (макс 25 сек, Telegram дає 60)
        try:
            future.result(timeout=25)
        except TimeoutError:
            logger.warning("⚠️ Обробка webhook перевищила таймаут 25с")
        except Exception as e:
            logger.error(f"❌ Помилка обробки update: {e}", exc_info=True)

        logger.info("✅ Webhook оброблено")
        return 'OK', 200

    except Exception as e:
        logger.error(f"❌ Помилка обробки webhook: {e}", exc_info=True)
        return 'Error', 500


@app.route(f'/cron/{CRON_SECRET}', methods=['POST'])
def cron():
    """Викликається зовнішнім планувальником (cron-job.org / PythonAnywhere Scheduled Task)."""
    try:
        sent_count = scheduler.run_due()
        return {'processed': sent_count}, 200
    except Exception as e:
        logger.error(f"❌ Помилка cron-диспетчера: {e}", exc_info=True)
        return 'Error', 500


@app.route('/altegio/webhook', methods=['POST'])
def altegio_webhook():
    """Приймає події від Altegio (запис створено/змінено/видалено)."""
    try:
        payload = request.get_json(force=True, silent=True) or {}
        logger.info(f"📥 Altegio webhook: {payload}")
        # TODO: обробка запису в tracked_records (Фаза 2)
        return 'OK', 200
    except Exception as e:
        logger.error(f"❌ Помилка обробки Altegio webhook: {e}", exc_info=True)
        return 'Error', 500


if __name__ == '__main__':
    # Для локального тестування
    app.run(debug=True, port=5000)