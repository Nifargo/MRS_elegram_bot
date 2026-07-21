"""Єдина точка реєстрації всіх handler-ів (webhook_bot.py і bot.py)."""
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters

from handlers import ai_chat, booking, my_bookings, pets, registration
from handlers.menu import BTN_BOOK, BTN_MY_BOOKINGS, BTN_MY_PETS, BTN_PRICE


def register_handlers(application: Application) -> None:
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
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_MY_BOOKINGS}$"), my_bookings.show_bookings))
    application.add_handler(CallbackQueryHandler(my_bookings.handle_callback, pattern=r"^mb_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat.handle_message))