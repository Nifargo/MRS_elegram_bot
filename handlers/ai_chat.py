"""AI-чат: все, що не кнопки меню і не команди, йде в Groq."""
import logging

from groq import RateLimitError
from telegram import Update
from telegram.ext import ContextTypes

from groq_client import get_response
from handlers.common import show_menu_button
from handlers.menu import is_menu_button, handle_menu_button
from services import ai_context, ai_guard
from services.notifications import notify_admins_async

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник текстових повідомлень поза діалогами (меню або AI)."""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Текст повідомлення в лог не пишемо: клієнти вписують туди імена й телефони.
    logger.info(f"📨 Повідомлення від {user_id}: {len(user_message)} символів")

    await show_menu_button(context.bot, update.effective_chat.id)

    if is_menu_button(user_message):
        await handle_menu_button(update, context)
        return

    if not ai_guard.allow_message(user_id):
        logger.info(f"Особистий ліміт AI вичерпано для {user_id}")
        await update.message.reply_text(ai_guard.AI_UNAVAILABLE_TEXT)
        return

    ctx = ai_context.for_user(user_id)

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        reply = await get_response(user_id, user_message[:ai_guard.MAX_INPUT_CHARS], ctx.text)
    except RateLimitError as e:
        # Квота Groq спільна для всіх клієнтів. «Спробуйте ще раз» тут не
        # допоможе, тож даємо телефон; адмінам піде дайджест о 18:30.
        ai_guard.record_quota_block(user_id, str(e))
        logger.warning(f"Groq 429 для {user_id}: {str(e)[:200]}")
        await update.message.reply_text(ai_guard.AI_UNAVAILABLE_TEXT)
        return
    except Exception as e:
        logger.error(f"❌ Помилка в handle_message: {e}", exc_info=True)
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте ще раз.")
        return

    unknown = ai_guard.unknown_amounts(reply, ctx.amounts)
    if unknown:
        logger.warning(f"AI назвав суми поза контекстом {sorted(unknown)} — відповідь підмінено")
        if ai_guard.record_guard_trip():
            await notify_admins_async(
                context.bot,
                "⚠️ AI-консультант часто називає суми, яких немає в прайсі — "
                "перевірте промпт і модель Groq.",
            )
        reply = ai_guard.price_fallback(ctx.price_lines)
    else:
        reply = ai_guard.strip_foreign_links(reply)

    try:
        await update.message.reply_text(reply)
        logger.info(f"✅ Відповідь надіслано користувачу {user_id}")
    except Exception as e:
        logger.error(f"❌ Не вдалось надіслати відповідь {user_id}: {e}", exc_info=True)
