# Graph Report - .  (2026-07-23)

## Corpus Check
- Corpus is ~21,267 words - fits in a single context window. You may not need a graph.

## Summary
- 502 nodes · 1009 edges · 45 communities (18 shown, 27 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Client & Pet Data Layer (dbclient.py)|Client & Pet Data Layer (db/client.py)]]
- [[_COMMUNITY_Booking Flow Core|Booking Flow Core]]
- [[_COMMUNITY_Common Validators & Formatting|Common Validators & Formatting]]
- [[_COMMUNITY_Booking DateTime Handling|Booking Date/Time Handling]]
- [[_COMMUNITY_Pet Card Editing|Pet Card Editing]]
- [[_COMMUNITY_Altegio API Client|Altegio API Client]]
- [[_COMMUNITY_Admin Notifications & Scheduler|Admin Notifications & Scheduler]]
- [[_COMMUNITY_Bot Entry Points (bot.pywebhook_bot.py)|Bot Entry Points (bot.py/webhook_bot.py)]]
- [[_COMMUNITY_AI Chat (Groq) Integration|AI Chat (Groq) Integration]]
- [[_COMMUNITY_Groq Client & Help Phone|Groq Client & Help Phone]]
- [[_COMMUNITY_Altegio Webhook Ingestion|Altegio Webhook Ingestion]]
- [[_COMMUNITY_Booking Breed-Fallback Suggestions|Booking Breed-Fallback Suggestions]]
- [[_COMMUNITY_Claude Code Hooks Registry|Claude Code Hooks Registry]]
- [[_COMMUNITY_Claude Settings Structure|Claude Settings Structure]]
- [[_COMMUNITY_Altegio Pets Comment Sync|Altegio Pets Comment Sync]]
- [[_COMMUNITY_Webhook Registration Script|Webhook Registration Script]]
- [[_COMMUNITY_Read-Tool Guard Hook|Read-Tool Guard Hook]]
- [[_COMMUNITY_Destructive-Command Block Hook|Destructive-Command Block Hook]]
- [[_COMMUNITY_Format-on-Save Hook|Format-on-Save Hook]]
- [[_COMMUNITY_RTK Rewrite Hook|RTK Rewrite Hook]]
- [[_COMMUNITY_Context Recovery Hook|Context Recovery Hook]]
- [[_COMMUNITY_Client Schema & Migration|Client Schema & Migration]]
- [[_COMMUNITY_Tracked Records Schema & Migration|Tracked Records Schema & Migration]]
- [[_COMMUNITY_Phase 11 Staff Selection Notes|Phase 11 Staff Selection Notes]]
- [[_COMMUNITY_Graphify Reminder Hook|Graphify Reminder Hook]]
- [[_COMMUNITY_Protect-Files Hook|Protect-Files Hook]]
- [[_COMMUNITY_RTK Suggest Hook|RTK Suggest Hook]]
- [[_COMMUNITY_Warn-Large-Files Hook|Warn-Large-Files Hook]]
- [[_COMMUNITY_Welcome Message Constant|Welcome Message Constant]]
- [[_COMMUNITY_Groq Client Instance|Groq Client Instance]]
- [[_COMMUNITY_Pets Schema|Pets Schema]]
- [[_COMMUNITY_Visit Extras Schema|Visit Extras Schema]]
- [[_COMMUNITY_Ratings Schema|Ratings Schema]]
- [[_COMMUNITY_Notifications Schema|Notifications Schema]]
- [[_COMMUNITY_Chat Messages Schema|Chat Messages Schema]]
- [[_COMMUNITY_Pet Date Formatting|Pet Date Formatting]]
- [[_COMMUNITY_Ideas Doc|Ideas Doc]]
- [[_COMMUNITY_Idea Photo Consultations|Idea: Photo Consultations]]
- [[_COMMUNITY_Idea Google Calendar Integration|Idea: Google Calendar Integration]]
- [[_COMMUNITY_Idea Location Buttons|Idea: Location Buttons]]
- [[_COMMUNITY_Idea FAQ Quick Replies|Idea: FAQ Quick Replies]]
- [[_COMMUNITY_Idea Popular Questions Stats|Idea: Popular Questions Stats]]
- [[_COMMUNITY_Idea Appointment Reminders|Idea: Appointment Reminders]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 49 edges
2. `handle_callback()` - 32 edges
3. `AltegioError` - 29 edges
4. `handle_callback()` - 27 edges
5. `InlineKeyboardButton` - 22 edges
6. `Update` - 19 edges
7. `int` - 19 edges
8. `int` - 18 edges
9. `DEFAULT_TYPE` - 18 edges
10. `register_handlers()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Altegio — єдине джерело правди` --rationale_for--> `upsert_tracked_record()`  [INFERRED]
  PLAN.md → db/client.py
- `Фаза 4 — Автоматичні нагадування + оцінки` --conceptually_related_to--> `upsert_tracked_record()`  [INFERRED]
  PLAN.md → db/client.py
- `handle_callback()` --implements--> `Фаза 2 — Онлайн-запис на грумінг`  [EXTRACTED]
  handlers/booking.py → PLAN.md
- `Патерн booking_incomplete (за зразком form_incomplete)` --rationale_for--> `schedule_booking_incomplete()`  [EXTRACTED]
  PLAN.md → services/notifications.py
- `handle_callback()` --implements--> `Фаза 9 — Зв'язок з адміністратором`  [EXTRACTED]
  handlers/booking.py → PLAN.md

## Hyperedges (group relationships)
- **Telegram Webhook Deployment Flow** — wsgi_application, webhook_bot_app, webhook_bot_webhook, set_webhook_set_webhook, config_telegram_token [INFERRED 0.85]
- **Altegio Webhook Ingestion Flow** — webhook_bot_altegio_webhook_route, config_altegio_webhook_secret, services_altegio_webhook_process_event, db_schema_tracked_records, plan_phase_2 [INFERRED 0.85]
- **PreToolUse Bash hook pipeline (block → suggest → rewrite)** — claude_settings, hooks_block_destructive_commands, hooks_rtk_suggest, hooks_rtk_rewrite [EXTRACTED 1.00]
- **Registration ConversationHandler state flow (phone -> location -> name -> pets)** — handlers_registration_conversation, handlers_registration_start, handlers_registration_got_phone, handlers_registration_got_location, handlers_registration_got_name, handlers_registration_got_pet_name, handlers_registration_got_pet_breed, handlers_registration_got_pet_birth, handlers_registration_got_pet_weight, handlers_registration_got_pet_allergies, handlers_registration_got_pet_behavior, handlers_registration_got_pet_photo, handlers_registration_got_add_more, handlers_registration_cancel [EXTRACTED 1.00]
- **my_bookings.py delegates client resolution and repeat-booking to booking.py** — handlers_my_bookings_handle_callback, handlers_booking_resolve_altegio_client_id, handlers_booking_start_from_pet_and_service, db_client_get_tracked_record_by_id [INFERRED 0.85]
- **Telegram update dispatch chain wired in register_handlers (order-dependent)** — handlers_setup_register_handlers, handlers_registration_conversation, handlers_pets_edit_conversation, handlers_pets_show_pets, handlers_pets_handle_callback, handlers_booking_book_start, handlers_booking_price_start, handlers_booking_handle_callback, handlers_my_bookings_show_bookings, handlers_my_bookings_handle_callback, handlers_ai_chat_handle_message [EXTRACTED 1.00]
- **Cron-driven booking_incomplete admin nudge flow** — handlers_booking__start, services_notifications_schedule_booking_incomplete, services_scheduler__handle_booking_incomplete, db_client_has_tracked_record_since [INFERRED 0.85]

## Communities (45 total, 27 thin omitted)

### Community 0 - "Client & Pet Data Layer (db/client.py)"
Cohesion: 0.05
Nodes (59): ALTEGIO_LOCATIONS, create_client_record(), create_notification(), create_pet(), delete_pet(), get_client_by_id(), get_client_by_phone(), get_client_by_tg_id() (+51 more)

### Community 1 - "Booking Flow Core"
Cohesion: 0.10
Nodes (56): _ask_category, _ask_date, _ask_time, _category_keyboard, _confirm_booking, _format_price, _location_name, _select_service (+48 more)

### Community 2 - "Common Validators & Formatting"
Cohesion: 0.13
Nodes (46): parse_weight(), float, int, Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, Викликати Telegram-запит (reply_text/reply_location/...) з повторами.      Прокс, with_retry(), _ask_location, _ask_pet_photo (+38 more)

### Community 3 - "Booking Date/Time Handling"
Cohesion: 0.09
Nodes (44): datetime, Exception, bool, format_date_label(), parse_iso_datetime(), str, Спільні валідатори полів анкети та карток улюбленців., 2026-08-01' -> '01.08 Сб' (для кнопок вибору дати). (+36 more)

### Community 4 - "Pet Card Editing"
Cohesion: 0.12
Nodes (34): date, parse_date(), bool, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні., _card_keyboard, _card_text, _delete_confirm_keyboard, _edit_keyboard (+26 more)

### Community 5 - "Altegio API Client"
Cohesion: 0.15
Nodes (34): _request, cancel_record(), create_client(), create_record(), find_available_staff_for_slot(), find_client_by_phone(), get_available_dates(), get_available_times() (+26 more)

### Community 6 - "Admin Notifications & Scheduler"
Cohesion: 0.08
Nodes (29): ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, CRON_SECRET, Патерн booking_incomplete (за зразком form_incomplete), notify_admins(), notify_admins_async(), bool, int (+21 more)

### Community 7 - "Bot Entry Points (bot.py/webhook_bot.py)"
Cohesion: 0.08
Nodes (27): Application, main(), Запуск бота (polling, для локальної розробки)., altegio_webhook_route(), cron(), ensure_initialized(), ensure_initialized_with_retries(), index() (+19 more)

### Community 8 - "AI Chat (Groq) Integration"
Cohesion: 0.10
Nodes (20): main() (polling entrypoint), SYSTEM_PROMPT, TELEGRAM_TOKEN, chat_histories (in-memory per-user dict), get_response(), Python dependencies list, python-3.11.0 runtime pin, check_webhook() (+12 more)

### Community 9 - "Groq Client & Help Phone"
Cohesion: 0.12
Nodes (19): HELP_PHONE, clear_chat_history(), get_response(), Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., int, str, handle_message() (+11 more)

### Community 10 - "Altegio Webhook Ingestion"
Cohesion: 0.20
Nodes (14): ALTEGIO_WEBHOOK_SECRET, normalize_phone(), Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на українс, _format_dt, _handle, _location_name, _format_dt(), _handle() (+6 more)

### Community 11 - "Booking Breed-Fallback Suggestions"
Cohesion: 0.18
Nodes (12): _ask_service, _category_type_key, _generic_breed_services, _match_services_by_breed, _service_row, _show_generic_fallback, _show_level_suggestion, _show_service_page (+4 more)

### Community 13 - "Claude Settings Structure"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 14 - "Altegio Pets Comment Sync"
Cohesion: 0.24
Nodes (10): _merge_comment, _pet_line, _merge_comment(), _pet_line(), bool, str, Синхронізація даних улюбленців у картку клієнта Altegio.  Altegio API не має окр, Зберегти текст адміністратора, замінити/додати лише блок бота. (+2 more)

### Community 15 - "Webhook Registration Script"
Cohesion: 0.29
Nodes (7): check_webhook(), get_webhook_info(), Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli, set_webhook(), str

### Community 16 - "Read-Tool Guard Hook"
Cohesion: 0.67
Nodes (3): deny(), main(), output

## Ambiguous Edges - Review These
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to

## Knowledge Gaps
- **78 isolated node(s):** `str`, `int`, `bool`, `str`, `allow` (+73 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `register_handlers()` connect `Bot Entry Points (bot.py/webhook_bot.py)` to `Booking Flow Core`, `Booking Date/Time Handling`, `Pet Card Editing`, `AI Chat (Groq) Integration`, `Groq Client & Help Phone`?**
  _High betweenness centrality (0.210) - this node is a cross-community bridge._
- **Why does `handle_callback()` connect `Booking Flow Core` to `Client & Pet Data Layer (db/client.py)`, `Common Validators & Formatting`, `Bot Entry Points (bot.py/webhook_bot.py)`, `Groq Client & Help Phone`, `Booking Breed-Fallback Suggestions`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Booking Date/Time Handling` to `Booking Flow Core`, `Common Validators & Formatting`, `Altegio API Client`, `Altegio Pets Comment Sync`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `AltegioError` (e.g. with `DEFAULT_TYPE` and `str`) actually correct?**
  _`AltegioError` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `InlineKeyboardButton` (e.g. with `AltegioError` and `show_bookings()`) actually correct?**
  _`InlineKeyboardButton` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `str`, `Отримати відповідь від Groq для повідомлення користувача.`, `Очистити історію чату для користувача.` to the rest of the system?**
  _181 weakly-connected nodes found - possible documentation gaps or missing edges._