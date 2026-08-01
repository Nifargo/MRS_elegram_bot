"""AI-чат: все, що не кнопки меню і не команди, йде в Groq."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from groq_client import get_response
from handlers.common import show_menu_button
from handlers.menu import is_menu_button, handle_menu_button

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник текстових повідомлень поза діалогами (меню або AI)."""
    user_id = update.effective_user.id
    user_message = update.message.text

    logger.info(f"📨 Повідомлення від {user_id}: {user_message}")

    await show_menu_button(context.bot, update.effective_chat.id)

    if is_menu_button(user_message):
        await handle_menu_button(update, context)
        return

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = await get_response(user_id, user_message)
        await update.message.reply_text(response)
        logger.info(f"✅ Відповідь Groq надіслано користувачу {user_id}")
    except Exception as e:
        logger.error(f"❌ Помилка в handle_message: {e}", exc_info=True)
        try:
            await update.message.reply_text("Вибачте, сталася помилка. Спробуйте ще раз.")
        except Exception:
            pass