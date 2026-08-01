"""Єдина точка реєстрації всіх handler-ів (webhook_bot.py і bot.py)."""
# from telegram import BotCommand, MenuButtonCommands
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters

from handlers import ai_chat, booking, my_bookings, nearest_slots, pets, rating, registration
from handlers.error_handler import handle_error
from handlers.menu import BTN_BOOK, BTN_MY_BOOKINGS, BTN_MY_PETS, BTN_NEAREST, BTN_PRICE


async def post_init(application: Application) -> None:
    """Кнопка «Меню» біля поля вводу — вимкнено (для нового чату Telegram і так
    показує нативну кнопку «СТАРТ»; розкоментувати, якщо знадобиться меню команд
    і посеред флоу з reply/inline-клавіатурою).
    """
    # await application.bot.set_my_commands([
    #     BotCommand("start", "🐾 Почати або перезапустити анкету"),
    #     BotCommand("cancel", "❌ Скасувати поточну дію"),
    # ])
    # await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


def register_handlers(application: Application) -> None:
    application.add_error_handler(handle_error)

    # Порядок важливий: діалоги (анкета, редагування) мають перехоплювати
    # повідомлення раніше за загальний AI-обробник.
    application.add_handler(registration.conversation)  # містить /start
    application.add_handler(pets.edit_conversation)
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_MY_PETS}$"), pets.show_pets))
    application.add_handler(CallbackQueryHandler(
        pets.handle_callback,
        pattern=r"^pet_(list$|show:|edit:|delete:|delete_confirm:)",
    ))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_BOOK}$"), booking.book_start))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_PRICE}$"), booking.price_start))
    application.add_handler(CallbackQueryHandler(booking.handle_callback, pattern=r"^bk_"))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_NEAREST}$"), nearest_slots.start))
    application.add_handler(CallbackQueryHandler(nearest_slots.handle_callback, pattern=r"^ns_"))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_MY_BOOKINGS}$"), my_bookings.show_bookings))
    application.add_handler(CallbackQueryHandler(my_bookings.handle_callback, pattern=r"^mb_"))
    application.add_handler(CallbackQueryHandler(rating.handle_callback, pattern=r"^rt_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat.handle_message))