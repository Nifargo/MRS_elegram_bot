# Graph Report - grooming-telegram-bot  (2026-08-01)

## Corpus Check
- 50 files · ~28,509 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 802 nodes · 1870 edges · 59 communities (33 shown, 26 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ebf36ed0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Client & Vaccine Sync Helpers|Client & Vaccine Sync Helpers]]
- [[_COMMUNITY_Booking Flow — Service & Client Resolution|Booking Flow — Service & Client Resolution]]
- [[_COMMUNITY_Common Validators & Telegram Retry|Common Validators & Telegram Retry]]
- [[_COMMUNITY_Altegio API Client|Altegio API Client]]
- [[_COMMUNITY_Altegio Webhook Handling|Altegio Webhook Handling]]
- [[_COMMUNITY_Deployment Guide (PythonAnywhere)|Deployment Guide (PythonAnywhere)]]
- [[_COMMUNITY_Project Plan & Architecture|Project Plan & Architecture]]
- [[_COMMUNITY_Booking Flow — Location & Staff Steps|Booking Flow — Location & Staff Steps]]
- [[_COMMUNITY_Supabase DB Client (PetsClients)|Supabase DB Client (Pets/Clients)]]
- [[_COMMUNITY_Pet Card UI & Editing|Pet Card UI & Editing]]
- [[_COMMUNITY_Claude Code Hooks|Claude Code Hooks]]
- [[_COMMUNITY_Groq AI Chat|Groq AI Chat]]
- [[_COMMUNITY_Notification Scheduler|Notification Scheduler]]
- [[_COMMUNITY_Bot Entrypoints & Handler Setup|Bot Entrypoints & Handler Setup]]
- [[_COMMUNITY_Rating & Review Flow|Rating & Review Flow]]
- [[_COMMUNITY_Flask Webhook Server|Flask Webhook Server]]
- [[_COMMUNITY_Notifications DB & Migrations|Notifications DB & Migrations]]
- [[_COMMUNITY_Claude Hooks Settings|Claude Hooks Settings]]
- [[_COMMUNITY_Notification State Helpers|Notification State Helpers]]
- [[_COMMUNITY_Event Loop & Initialization|Event Loop & Initialization]]
- [[_COMMUNITY_Webhook Registration Script|Webhook Registration Script]]
- [[_COMMUNITY_Feature Ideas Backlog|Feature Ideas Backlog]]
- [[_COMMUNITY_MCP Server Config|MCP Server Config]]
- [[_COMMUNITY_Deployment Config & Rationale|Deployment Config & Rationale]]
- [[_COMMUNITY_Daily Cron Task State|Daily Cron Task State]]
- [[_COMMUNITY_Booking Widget Redesign (Phase 2)|Booking Widget Redesign (Phase 2)]]
- [[_COMMUNITY_Local Claude Settings|Local Claude Settings]]
- [[_COMMUNITY_MCP Server Permissions|MCP Server Permissions]]
- [[_COMMUNITY_Clients Table Migration|Clients Table Migration]]
- [[_COMMUNITY_Tracked Records Migration|Tracked Records Migration]]
- [[_COMMUNITY_Welcome Message|Welcome Message]]
- [[_COMMUNITY_Groq Client Instance|Groq Client Instance]]
- [[_COMMUNITY_Pets Table|Pets Table]]
- [[_COMMUNITY_Visit Extras Table|Visit Extras Table]]
- [[_COMMUNITY_Ratings Table|Ratings Table]]
- [[_COMMUNITY_Notifications Table|Notifications Table]]
- [[_COMMUNITY_Chat Messages Table|Chat Messages Table]]
- [[_COMMUNITY_Ideas Backlog Doc|Ideas Backlog Doc]]
- [[_COMMUNITY_Photo Consultation Idea|Photo Consultation Idea]]
- [[_COMMUNITY_Google Calendar Idea|Google Calendar Idea]]
- [[_COMMUNITY_Geolocation Buttons Idea|Geolocation Buttons Idea]]
- [[_COMMUNITY_FAQ Menu Idea|FAQ Menu Idea]]
- [[_COMMUNITY_Popular Questions Stats Idea|Popular Questions Stats Idea]]
- [[_COMMUNITY_Reminder Notifications Idea|Reminder Notifications Idea]]
- [[_COMMUNITY_Groq API Key|Groq API Key]]
- [[_COMMUNITY_Altegio Partner Token|Altegio Partner Token]]
- [[_COMMUNITY_Altegio User Token|Altegio User Token]]
- [[_COMMUNITY_Supabase URL|Supabase URL]]
- [[_COMMUNITY_Supabase Service Key|Supabase Service Key]]
- [[_COMMUNITY_Editable Pet Fields|Editable Pet Fields]]
- [[_COMMUNITY_Main Menu Keyboard|Main Menu Keyboard]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 72 edges
2. `with_retry()` - 70 edges
3. `AltegioError` - 45 edges
4. `InlineKeyboardButton` - 35 edges
5. `register_handlers()` - 26 edges
6. `Update` - 25 edges
7. `int` - 25 edges
8. `DEFAULT_TYPE` - 24 edges
9. `handle_callback()` - 24 edges
10. `show_menu_button()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `location_name()` --semantically_similar_to--> `_location_name()`  [INFERRED] [semantically similar]
  handlers/booking.py → services/altegio_webhook.py
- `with_retry()` --semantically_similar_to--> `send_telegram_message()`  [INFERRED] [semantically similar]
  handlers/common.py → services/notifications.py
- `Altegio як єдине джерело правди (архітектурний принцип)` --rationale_for--> `upsert_tracked_record()`  [EXTRACTED]
  PLAN.md → db/client.py
- `str` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py
- `float` --uses--> `AltegioError`  [INFERRED]
  handlers/nearest_slots.py → services/altegio.py

## Hyperedges (group relationships)
- **Find-or-create Altegio client pattern (registration vs booking)** — registration_ensure_altegio_link, registration_search_altegio_client, booking_resolve_altegio_client_id [INFERRED 0.80]
- **Repeat-last-booking flow (my_bookings → booking entry point)** — booking_start_from_pet_and_service, my_bookings_repeat_last_booking, my_bookings_handle_callback [EXTRACTED 0.90]
- **staff_id column: migration → webhook ingestion → booking confirm → reschedule** — migrations_006_tracked_records_staff_id_column, altegio_webhook_handle, booking_confirm_booking, my_bookings_confirm_reschedule [EXTRACTED 0.90]

## Communities (59 total, 26 thin omitted)

### Community 0 - "Client & Vaccine Sync Helpers"
Cohesion: 0.08
Nodes (57): normalize_phone(), to_kyiv_iso(), datetime, get_client_by_tg_id(), get_last_past_tracked_record(), Знайти клієнта за Telegram user_id. Повертає None, якщо не знайдено., Останній минулий (не скасований) запис клієнта — для «Повторити останній запис»., Exception (+49 more)

### Community 1 - "Booking Flow — Service & Client Resolution"
Cohesion: 0.09
Nodes (74): _ask_service(), _confirm_booking(), format_price(), generic_breed_services(), location_name(), match_services_by_breed(), registered_client_pets(), resolve_altegio_client_id() (+66 more)

### Community 2 - "Common Validators & Telegram Retry"
Cohesion: 0.10
Nodes (66): parse_weight(), with_retry(), hide_menu_button(), float, int, Приховати нативну кнопку «Меню» (/start, /cancel) на час активного флоу     (анк, Показати кнопку «Меню» — клієнт поза флоу (вільний AI-чат чи заглушки меню)., Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1 (+58 more)

### Community 3 - "Altegio API Client"
Cohesion: 0.06
Nodes (56): create_client_record(), Створити порожній запис клієнта (реєстрацію заповнюємо покроково)., cancel_record(), create_client(), create_record(), find_available_staff_for_slot(), find_client_by_phone(), get_available_dates() (+48 more)

### Community 4 - "Altegio Webhook Handling"
Cohesion: 0.16
Nodes (21): _handle(), process_event(), Кешований запис за id з Altegio. None, якщо ще не синхронізований., Створити або оновити кеш запису (fields повинні містити altegio_record_id)., upsert_tracked_record(), normalize_phone(), Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на українс, Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на українс (+13 more)

### Community 5 - "Deployment Guide (PythonAnywhere)"
Cohesion: 0.06
Nodes (38): 1. Завантажити зміни на GitHub (на Mac), 1. Напиши боту в Telegram, 2. Оновити код на PythonAnywhere, 2. Перевір webhook статус, 3. Зупинити старий polling бот (якщо працює), 3. Подивись логи Flask, 4. Налаштувати Web App на PythonAnywhere, 5. Налаштувати WSGI файл (+30 more)

### Community 6 - "Project Plan & Architecture"
Cohesion: 0.06
Nodes (33): 0. Поточний стан і ключове рішення, Altegio API — що використовуємо, code:block1 (grooming-telegram-bot/), code:block2 (clients        id, tg_user_id (unique), altegio_client_id, p), code:block3 (Фаза 0 ✅ (фундамент + Altegio API + вебхуки)), Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint, UI бота: Inline-кнопки + ConversationHandler, Архітектурні рішення (+25 more)

### Community 7 - "Booking Flow — Location & Staff Steps"
Cohesion: 0.16
Nodes (42): _ask_location(), _ask_service(), _ask_staff(), _breed_eligible_levels(), _category_level(), _confirm(), handle_callback(), _level_of_text() (+34 more)

### Community 8 - "Supabase DB Client (Pets/Clients)"
Cohesion: 0.11
Nodes (28): create_pet(), create_rating(), delete_pet(), get_pet(), get_pets_by_client(), get_rating(), get_tracked_record(), get_tracked_record_by_id() (+20 more)

### Community 9 - "Pet Card UI & Editing"
Cohesion: 0.14
Nodes (31): parse_weight(), Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, _card_keyboard(), _card_text(), _delete_confirm_keyboard(), edit_cancel(), edit_field_start() (+23 more)

### Community 10 - "Claude Code Hooks"
Cohesion: 0.08
Nodes (15): .claude/settings.json (hook registration), deny(), find_project_root(), find_project_root(), deny(), main(), output, _rtk_audit_log() (+7 more)

### Community 11 - "Groq AI Chat"
Cohesion: 0.06
Nodes (53): bool, ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, SYSTEM_PROMPT, clear_chat_history(), get_response(), Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача. (+45 more)

### Community 12 - "Notification Scheduler"
Cohesion: 0.13
Nodes (26): get_client_by_id(), Знайти клієнта за внутрішнім id., _clear_booking_state(), _handle_booking_incomplete(), _handle_form_incomplete(), run_due(), _clear_booking_state(), _handle_booking_incomplete() (+18 more)

### Community 13 - "Bot Entrypoints & Handler Setup"
Cohesion: 0.12
Nodes (24): parse_date(), date, get_clients_with_altegio_link(), Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)., parse_date(), bool, date, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні. (+16 more)

### Community 14 - "Rating & Review Flow"
Cohesion: 0.16
Nodes (13): GOOGLE_MAPS_REVIEW_URLS, HELP_PHONE, handle_callback(), _owns_record(), bool, DEFAULT_TYPE, int, Update (+5 more)

### Community 15 - "Flask Webhook Server"
Cohesion: 0.14
Nodes (18): CRON_SECRET, cron(), ensure_initialized_with_retries(), index(), ensure_initialized() з повторами - проксі PythonAnywhere інколи віддає 503., ensure_initialized() з повторами - проксі PythonAnywhere інколи віддає 503., Головна сторінка - перевірка що бот працює., Головна сторінка - перевірка що бот працює. (+10 more)

### Community 16 - "Notifications DB & Migrations"
Cohesion: 0.20
Nodes (14): ensure_initialized(), initialize_application(), _is_loop_alive(), Запустити event loop в окремому потоці., Ініціалізувати Telegram Application., Перевірити чи event loop живий і працює., Перевірити чи event loop живий і працює., Переконатись що бот ініціалізований. Перезапускає якщо event loop помер. (+6 more)

### Community 17 - "Claude Hooks Settings"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 18 - "Notification State Helpers"
Cohesion: 0.13
Nodes (18): create_notification(), delete_pending_notifications_for_record(), get_client_by_phone(), has_pending_notification(), has_tracked_record_since(), bool, str, Чи з'явився активний запис клієнта після вказаного часу (перевірка, чи флоу запи (+10 more)

### Community 19 - "Event Loop & Initialization"
Cohesion: 0.18
Nodes (12): book_start() — «📅 Записатись», price_start() — «💰 Дізнатись вартість», ALTEGIO_BOOKING_WIDGET_URL, conversation (registration ConversationHandler), show_bookings() — «🗓 Мої записи», start() — «🔥 Найближчі віконця», edit_conversation (ConversationHandler), show_pets() — «🐾 Мої улюбленці» (+4 more)

### Community 20 - "Webhook Registration Script"
Cohesion: 0.26
Nodes (12): TELEGRAM_TOKEN, check_webhook(), get_webhook_info(), Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli, set_webhook(), check_webhook() (+4 more)

### Community 21 - "Feature Ideas Backlog"
Cohesion: 0.25
Nodes (7): 📍 Кнопки з локаціями салонів, 🔔 Нагадування про запис, 📸 Обробка фото, 📊 Статистика популярних запитань, 💬 Швидкі відповіді (FAQ кнопки), 💡 Ідеї для покращення бота Mr.Snoopy Grooming, 📅 Інтеграція з Google Calendar

### Community 22 - "MCP Server Config"
Cohesion: 0.29
Nodes (6): Authorization, mcpServers, supabase, headers, type, url

### Community 23 - "Deployment Config & Rationale"
Cohesion: 0.50
Nodes (3): Answer, Q: Чому register_handlers() з'єднує Bot Entrypoints & Handler Setup з 10 іншими спільнотами?, Source Nodes

### Community 24 - "Daily Cron Task State"
Cohesion: 0.29
Nodes (8): get_cron_last_run(), Дата (ISO) останнього запуску щоденної задачі з цим ключем. None, якщо ще не зап, Позначити, що щоденна задача виконана сьогодні (ISO-дата)., Дата (ISO) останнього запуску щоденної задачі з цим ключем. None, якщо ще не зап, Позначити, що щоденна задача виконана сьогодні (ISO-дата)., set_cron_last_run(), cron_state table, _run_daily_tasks()

### Community 53 - "Community 53"
Cohesion: 0.22
Nodes (4): BaseHTTPRequestHandler, _FlakyHandler, Self-check: send_telegram_message() retries transient 503s via the Session-level, RetryTest

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (8): Application, main(), Запуск бота (polling, для локальної розробки)., post_init(), Єдина точка реєстрації всіх handler-ів (webhook_bot.py і bot.py)., Глобальний дефолт кнопки «Меню» (/start, /cancel) для нових чатів.      Під час, register_handlers(), post_init()

### Community 56 - "Community 56"
Cohesion: 0.22
Nodes (9): get_due_notifications(), Перевірити і обробити всі прострочені сповіщення. Повертає їх кількість.      `a, Задачі, що виконуються раз на добу (а не при кожному 10-хвилинному тику).      Д, Перевірити і обробити всі прострочені сповіщення. Повертає їх кількість.      `a, Сповіщення, які вже пора відправити (status=pending, send_after <= зараз)., Сповіщення, які вже пора відправити (status=pending, send_after <= зараз)., Задачі, що виконуються раз на добу (а не при кожному 10-хвилинному тику).      Д, _run_daily_tasks() (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (7): main() (polling entrypoint), Python dependencies list, python-3.11.0 runtime pin, Flask app instance, WEBHOOK_SETUP.md (deployment guide), Webhook-over-polling rationale (PythonAnywhere free tier blocks polling), application (WSGI entry, binds webhook_bot.app)

### Community 58 - "Community 58"
Cohesion: 0.67
Nodes (3): altegio_webhook_route(), Приймає події від Altegio (запис створено/змінено/видалено)., Приймає події від Altegio (запис створено/змінено/видалено).

## Ambiguous Edges - Review These
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to

## Knowledge Gaps
- **117 isolated node(s):** `type`, `url`, `Authorization`, `allow`, `deny` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `register_handlers()` connect `Event Loop & Initialization` to `Client & Vaccine Sync Helpers`, `Booking Flow — Service & Client Resolution`, `Common Validators & Telegram Retry`, `Pet Card UI & Editing`, `Groq AI Chat`, `Rating & Review Flow`, `Notifications DB & Migrations`, `Community 55`, `Community 57`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Client & Vaccine Sync Helpers` to `Booking Flow — Service & Client Resolution`, `Common Validators & Telegram Retry`, `Altegio API Client`, `Booking Flow — Location & Staff Steps`, `Bot Entrypoints & Handler Setup`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `with_retry()` connect `Common Validators & Telegram Retry` to `Client & Vaccine Sync Helpers`, `Booking Flow — Service & Client Resolution`, `Booking Flow — Location & Staff Steps`, `Pet Card UI & Editing`, `Groq AI Chat`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `AltegioError` (e.g. with `DEFAULT_TYPE` and `str`) actually correct?**
  _`AltegioError` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `InlineKeyboardButton` (e.g. with `show_bookings()` and `_show_reschedule_date_page()`) actually correct?**
  _`InlineKeyboardButton` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `type`, `url`, `Authorization` to the rest of the system?**
  _294 weakly-connected nodes found - possible documentation gaps or missing edges._