import logging
from telegram import Update
from telegram.ext import Application

from config import TELEGRAM_TOKEN
from handlers.setup import register_handlers

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Запуск бота (polling, для локальної розробки)."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Ті самі обробники, що й у webhook_bot.py
    register_handlers(application)

    # Запустити бота
    logger.info("Бот запущено...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()