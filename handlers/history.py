"""Історія візитів («✂️ Історія», Фаза 5): минулі візити клієнта з Altegio.

Читання без дій над записами, тож ConversationHandler не потрібен — лише
пагінація. Зібраний список кешується в context.user_data["history"] на час
перегляду (той самий підхід, що дати/часи в handlers/booking.py): збір коштує
до 6 запитів до Altegio (пошук клієнта + записи по кожній філії), і платити цю
ціну на кожен тап «➡️ Давніші» ні до чого.

Улюбленця в картці візиту не показуємо: в Altegio немає зв'язки візит↔тварина,
а назва послуги і так містить породу («Мальтіпу до 4 кг»).

Callback data:
  hs_pg:<page> — сторінка списку
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import client as db
from handlers.common import with_retry
from services import visit_history
from services.altegio import AltegioError
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

PAGE_SIZE = 5


def _format_visit(visit: dict) -> str:
    starts_at = visit["starts_at"].astimezone(KYIV_TZ)
    titles = visit["service_titles"]
    lines = [
        f"📅 {starts_at.strftime('%d.%m.%Y')} о {starts_at.strftime('%H:%M')}",
        f"✂️ {' + '.join(titles) if titles else '—'}",
    ]
    if visit["staff_name"]:
        lines.append(f"👤 {visit['staff_name']}")
    lines.append(f"📍 {visit['location_title']}")
    if visit["cost"]:
        lines.append(f"💰 {visit['cost']} грн")
    return "\n".join(lines)


async def _show_page(message, context: ContextTypes.DEFAULT_TYPE, page: int) -> None:
    visits = context.user_data.get("history", [])
    start = page * PAGE_SIZE
    chunk = visits[start:start + PAGE_SIZE]
    if not chunk:
        await with_retry(message.reply_text, "Візитів не знайдено 😔")
        return

    header = f"✂️ Історія візитів ({len(visits)})"
    text = "\n\n".join([header] + [_format_visit(v) for v in chunk])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Новіші", callback_data=f"hs_pg:{page - 1}"))
    if start + PAGE_SIZE < len(visits):
        nav.append(InlineKeyboardButton("➡️ Давніші", callback_data=f"hs_pg:{page + 1}"))

    await with_retry(
        message.reply_text, text,
        reply_markup=InlineKeyboardMarkup([nav]) if nav else None,
    )


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка меню «✂️ Історія»."""
    client = db.get_client_by_tg_id(update.effective_user.id)
    if client is None or not client["registration_done"]:
        await with_retry(update.message.reply_text, "Спочатку заповнимо коротку анкету — надішліть /start 🐾")
        return

    # Збір по трьох філіях займає секунду-дві — без цього рядка бот виглядає «завислим».
    await with_retry(update.message.reply_text, "Шукаю ваші візити… ⏳")

    try:
        visits = visit_history.get_past_visits(client)
    except AltegioError as e:
        logger.error(f"Історія візитів клієнта {client['id']}: {e}")
        await with_retry(update.message.reply_text,
            "Не вдалося завантажити історію візитів 😔 Спробуйте пізніше або зверніться до "
            "адміністратора через «🆘 Допомога».",
        )
        return

    if not visits:
        await with_retry(update.message.reply_text,
            "Історія візитів поки порожня — вона з'явиться тут після першого візиту 🐾",
        )
        return

    context.user_data["history"] = visits
    await _show_page(update.message, context, 0)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await with_retry(query.answer)
    action, _, rest = query.data.partition(":")

    if action == "hs_pg":
        if "history" not in context.user_data:
            await with_retry(query.message.reply_text, "Список застарів — натисніть «✂️ Історія» ще раз.")
            return
        await _show_page(query.message, context, int(rest))
