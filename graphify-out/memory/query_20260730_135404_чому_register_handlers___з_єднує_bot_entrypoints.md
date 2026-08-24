---
type: "explain"
date: "2026-07-30T13:54:04.144413+00:00"
question: "Чому register_handlers() з'єднує Bot Entrypoints & Handler Setup з 10 іншими спільнотами?"
contributor: "graphify"
source_nodes: ["register_handlers", "post_init", "handlers_setup", "booking_book_start", "my_bookings_show_bookings", "pets_show_pets", "nearest_slots_search", "rating_handle_callback", "ai_chat_handle_message"]
---

# Q: Чому register_handlers() з'єднує Bot Entrypoints & Handler Setup з 10 іншими спільнотами?

## Answer

register_handlers() (handlers/setup.py) — єдина точка реєстрації всіх feature-handler-ів в Application (bot.py polling + webhook_bot.py webhook runtime). Реєструє: booking.py (book_start/price_start/callback), my_bookings.py (show_bookings/reschedule/cancel), pets.py (show_pets/edit), nearest_slots.py, rating.py (handle_callback gated by _owns_record), ai_chat.handle_message (фолбек, реєструється останнім). Висока betweenness centrality (0.160) через те, що це тонкий fan-out список — єдиний шлях, яким кожен модуль стає досяжним з live Telegram update, а не через важку бізнес-логіку.

## Source Nodes

- register_handlers
- post_init
- handlers_setup
- booking_book_start
- my_bookings_show_bookings
- pets_show_pets
- nearest_slots_search
- rating_handle_callback
- ai_chat_handle_message