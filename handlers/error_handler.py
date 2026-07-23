"""Глобальний обробник помилок PTB.

Без нього виняток, що вилетів з будь-якого handler-а (напр. Telegram API
відхилив запит після вичерпаних ретраїв у with_retry), PTB 21 просто логує і
"ковтає" — клієнт не отримує жодної відповіді, а помилка ніде не видна, крім
server.log.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from handlers.menu import MAIN_MENU
from services.notifications import notify_admins_async

logger = logging.getLogger(__name__)

FALLBACK_TEXT = "⚠️ Сталася технічна помилка. Спробуйте ще раз або скористайтесь меню нижче."


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"❌ Необроблений виняток: {context.error}", exc_info=context.error)

    await notify_admins_async(
        context.bot,
        f"⚠️ Помилка в боті: {context.error}\nUpdate: {update}",
    )

    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=FALLBACK_TEXT,
                reply_markup=MAIN_MENU,
            )
        except Exception as e:
            logger.error(f"Не вдалося надіслати fallback-повідомлення про помилку: {e}")
