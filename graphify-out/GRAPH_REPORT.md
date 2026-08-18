# Graph Report - .  (2026-08-18)

## Corpus Check
- 20 files · ~33,423 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 885 nodes · 1952 edges · 64 communities (34 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Booking and Price Flow|Booking and Price Flow]]
- [[_COMMUNITY_Visit History and Shared Validators|Visit History and Shared Validators]]
- [[_COMMUNITY_Supabase Data Access Layer|Supabase Data Access Layer]]
- [[_COMMUNITY_Bot Entrypoints and Webhooks|Bot Entrypoints and Webhooks]]
- [[_COMMUNITY_Slot Selection and Record Upsert|Slot Selection and Record Upsert]]
- [[_COMMUNITY_Webhook Reconciliation and Cancellation|Webhook Reconciliation and Cancellation]]
- [[_COMMUNITY_Client Registration Flow|Client Registration Flow]]
- [[_COMMUNITY_Breed-Based Service Matching|Breed-Based Service Matching]]
- [[_COMMUNITY_Pet Card Management|Pet Card Management]]
- [[_COMMUNITY_Deployment and Webhook Setup|Deployment and Webhook Setup]]
- [[_COMMUNITY_Plan Architecture Sections|Plan Architecture Sections]]
- [[_COMMUNITY_AI Chat Assistant|AI Chat Assistant]]
- [[_COMMUNITY_Claude Hooks Configuration|Claude Hooks Configuration]]
- [[_COMMUNITY_Rebook Promo Tests|Rebook Promo Tests]]
- [[_COMMUNITY_Altegio Truth and History Concepts|Altegio Truth and History Concepts]]
- [[_COMMUNITY_Booking Redesign and Management Concepts|Booking Redesign and Management Concepts]]
- [[_COMMUNITY_Notification Scheduler Dispatch|Notification Scheduler Dispatch]]
- [[_COMMUNITY_Admin Alerts and Error Handling|Admin Alerts and Error Handling]]
- [[_COMMUNITY_Free-Slot Rebook Promo|Free-Slot Rebook Promo]]
- [[_COMMUNITY_Daily Automation Concepts|Daily Automation Concepts]]
- [[_COMMUNITY_Altegio API Access and Risks|Altegio API Access and Risks]]
- [[_COMMUNITY_Claude Settings Permissions|Claude Settings Permissions]]
- [[_COMMUNITY_Registration and Handler Concepts|Registration and Handler Concepts]]
- [[_COMMUNITY_Reconciliation and Loyalty Concepts|Reconciliation and Loyalty Concepts]]
- [[_COMMUNITY_Visit Notification Concepts|Visit Notification Concepts]]
- [[_COMMUNITY_Promo Callback Ownership Checks|Promo Callback Ownership Checks]]
- [[_COMMUNITY_Pet Birthday Greetings|Pet Birthday Greetings]]
- [[_COMMUNITY_Telegram Retry Tests|Telegram Retry Tests]]
- [[_COMMUNITY_Improvement Ideas Backlog|Improvement Ideas Backlog]]
- [[_COMMUNITY_MCP Server Configuration|MCP Server Configuration]]
- [[_COMMUNITY_Birthday Unit Tests|Birthday Unit Tests]]
- [[_COMMUNITY_Graphify Query Memory|Graphify Query Memory]]
- [[_COMMUNITY_Thanks Rating Handler|Thanks Rating Handler]]
- [[_COMMUNITY_Local Claude Settings|Local Claude Settings]]
- [[_COMMUNITY_Tracked Records Table|Tracked Records Table]]
- [[_COMMUNITY_Supabase MCP Config|Supabase MCP Config]]
- [[_COMMUNITY_Clients Table|Clients Table]]
- [[_COMMUNITY_Welcome Message|Welcome Message]]
- [[_COMMUNITY_Groq Client Instance|Groq Client Instance]]
- [[_COMMUNITY_Pets Table|Pets Table]]
- [[_COMMUNITY_Visit Extras Table|Visit Extras Table]]
- [[_COMMUNITY_Ratings Table|Ratings Table]]
- [[_COMMUNITY_Notifications Table|Notifications Table]]
- [[_COMMUNITY_Chat Messages Table|Chat Messages Table]]
- [[_COMMUNITY_Registration Conversation|Registration Conversation]]
- [[_COMMUNITY_Ideas Backlog File|Ideas Backlog File]]
- [[_COMMUNITY_Photo Consultation Idea|Photo Consultation Idea]]
- [[_COMMUNITY_Google Calendar Idea|Google Calendar Idea]]
- [[_COMMUNITY_Location Buttons Idea|Location Buttons Idea]]
- [[_COMMUNITY_FAQ Menu Idea|FAQ Menu Idea]]
- [[_COMMUNITY_Question Statistics Idea|Question Statistics Idea]]
- [[_COMMUNITY_Appointment Reminder Idea|Appointment Reminder Idea]]
- [[_COMMUNITY_Groq API Key|Groq API Key]]
- [[_COMMUNITY_Altegio Partner Token|Altegio Partner Token]]
- [[_COMMUNITY_Altegio User Token|Altegio User Token]]
- [[_COMMUNITY_Supabase URL|Supabase URL]]
- [[_COMMUNITY_Supabase Service Key|Supabase Service Key]]
- [[_COMMUNITY_Editable Pet Fields|Editable Pet Fields]]
- [[_COMMUNITY_My Bookings Entry|My Bookings Entry]]
- [[_COMMUNITY_Main Menu Keyboard|Main Menu Keyboard]]
- [[_COMMUNITY_My Pets Entry|My Pets Entry]]
- [[_COMMUNITY_Pet Edit Conversation|Pet Edit Conversation]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 83 edges
2. `AltegioError` - 61 edges
3. `InlineKeyboardButton` - 35 edges
4. `process_record()` - 26 edges
5. `show_menu_button()` - 24 edges
6. `int` - 20 edges
7. `Update` - 20 edges
8. `int` - 20 edges
9. `handle_callback()` - 20 edges
10. `_confirm_booking()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Query memory: why register_handlers connects Bot Entrypoints community to 10 others` --references--> `start()`  [AMBIGUOUS]
  graphify-out/memory/query_20260730_135404_чому_register_handlers___з_єднує_bot_entrypoints.md → handlers/nearest_slots.py
- `location_name()` --semantically_similar_to--> `_location_name()`  [INFERRED] [semantically similar]
  handlers/booking.py → services/altegio_webhook.py
- `with_retry()` --semantically_similar_to--> `send_telegram_message()`  [INFERRED] [semantically similar]
  handlers/common.py → services/notifications.py
- `Phase 5 — Grooming Visit History` --references--> `services/test_visit_history.py (visit history unit tests)`  [EXTRACTED]
  PLAN.md → services/test_visit_history.py
- `Inline Buttons plus ConversationHandler UI Pattern` --references--> `handlers/setup.py (single handler registration point)`  [INFERRED]
  PLAN.md → handlers/setup.py

## Hyperedges (group relationships)
- **Cross-branch visit history read path (Phase 5)** — handlers_history_show_history, services_visit_history_get_past_visits, services_visit_history__branch_client_ids, services_altegio_find_client_by_phone, services_altegio_get_client_records, handlers_history__format_visit [EXTRACTED 1.00]
- **Daily cron task dispatch guarded by cron_state** — services_scheduler__run_daily_tasks, services_altegio_reconcile_reconcile_upcoming_records, services_birthday_send_birthday_greetings, services_rebook_promo_send_rebook_promos, db_client_get_cron_last_run, db_client_set_cron_last_run, services_scheduler_all_or_nothing_daily_contract [EXTRACTED 1.00]
- **Rebook promo send/dismiss lifecycle** — services_rebook_promo_send_rebook_promos, handlers_rebook_promo_handle_callback, handlers_rebook_promo__owning_client, migrations_008_phase7_rebook_promo_rebook_promo_dismissed_record_id, db_client_get_active_tracked_records_with_ends_at, db_client_update_client [INFERRED 0.85]
- **Visit Notification Lifecycle (schedule, remind, thank, nudge)** — plan_tracked_records_cache, plan_reminder_2h, plan_thanks_rating, plan_rebook_nudge, plan_idempotent_visit_notification_scheduling [EXTRACTED 1.00]
- **Breed-Based Service Selection Fallback Chain** — plan_breed_based_service_matching, plan_sibling_level_breed_fallback, plan_generic_breed_fallback, plan_phase_2_online_booking, plan_phase_11_nearest_slots [EXTRACTED 1.00]
- **Altegio State Synchronisation Safety Net** — plan_webhook_record_reconciliation, plan_daily_altegio_reconciliation, plan_tracked_records_cache, plan_risk_webhook_delivery_not_guaranteed, plan_cron_daily_task_gating [EXTRACTED 1.00]

## Communities (64 total, 30 thin omitted)

### Community 0 - "Booking and Price Flow"
Cohesion: 0.07
Nodes (96): _ask_service(), book_start() — «📅 Записатись», _confirm_booking(), format_price(), location_name(), price_start() — «💰 Дізнатись вартість», registered_client_pets(), resolve_altegio_client_id() (+88 more)

### Community 1 - "Visit History and Shared Validators"
Cohesion: 0.05
Nodes (60): parse_date(), date, get_clients_with_altegio_link(), Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)., bool, date, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні., _format_visit() (+52 more)

### Community 2 - "Supabase Data Access Layer"
Cohesion: 0.05
Nodes (60): bool, GOOGLE_MAPS_REVIEW_URLS, create_notification(), create_pet(), create_rating(), delete_pending_notifications_for_record(), delete_pet(), get_active_tracked_records_in_range() (+52 more)

### Community 3 - "Bot Entrypoints and Webhooks"
Cohesion: 0.05
Nodes (48): Application, main() (polling entrypoint), CRON_SECRET, TELEGRAM_TOKEN, main(), Запуск бота (polling, для локальної розробки)., Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц (+40 more)

### Community 4 - "Slot Selection and Record Upsert"
Cohesion: 0.09
Nodes (50): create_client_record(), Створити або оновити кеш запису (fields повинні містити altegio_record_id)., Створити порожній запис клієнта (реєстрацію заповнюємо покроково)., upsert_tracked_record(), booking._ask_date, booking._ask_time, booking._confirm_booking, my_bookings._ask_reschedule_date (+42 more)

### Community 5 - "Webhook Reconciliation and Cancellation"
Cohesion: 0.07
Nodes (41): normalize_phone(), datetime, get_client_by_phone(), Позначити статус запису (напр. cancelled при скасуванні в Altegio)., Знайти клієнта за телефоном (формат +380XXXXXXXXX). Для матчингу Altegio-вебхукі, update_tracked_record_status(), Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на українс, my_bookings._do_cancel (+33 more)

### Community 6 - "Client Registration Flow"
Cohesion: 0.11
Nodes (47): get_client_by_tg_id(), Знайти клієнта за Telegram user_id. Повертає None, якщо не знайдено., Оновити поля клієнта., update_client(), registration._ask_location, registration._ensure_altegio_link, registration._search_altegio_client, _ask_location() (+39 more)

### Community 7 - "Breed-Based Service Matching"
Cohesion: 0.12
Nodes (42): generic_breed_services(), match_services_by_breed(), slim_service(), bool, float, _weight_matches(), nearest_slots._ask_service, nearest_slots._breed_eligible_levels (+34 more)

### Community 8 - "Pet Card Management"
Cohesion: 0.10
Nodes (37): parse_weight(), float, Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, _card_keyboard(), _card_text(), _delete_confirm_keyboard(), edit_cancel(), edit_field_start() (+29 more)

### Community 9 - "Deployment and Webhook Setup"
Cohesion: 0.06
Nodes (35): 1. Завантажити зміни на GitHub (на Mac), 1. Напиши боту в Telegram, 2. Оновити код на PythonAnywhere, 2. Перевір webhook статус, 3. Зупинити старий polling бот (якщо працює), 3. Подивись логи Flask, 4. Налаштувати Web App на PythonAnywhere, 5. Налаштувати WSGI файл (+27 more)

### Community 10 - "Plan Architecture Sections"
Cohesion: 0.06
Nodes (33): 0. Поточний стан і ключове рішення, Altegio API — що використовуємо, code:block1 (grooming-telegram-bot/), code:block2 (clients        id, tg_user_id (unique), altegio_client_id, p), code:block3 (Фаза 0 ✅ (фундамент + Altegio API + вебхуки)), Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint, UI бота: Inline-кнопки + ConversationHandler, Архітектурні рішення (+25 more)

### Community 11 - "AI Chat Assistant"
Cohesion: 0.10
Nodes (22): HELP_PHONE, SYSTEM_PROMPT, Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., chat_histories (in-memory per-user dict), clear_chat_history(), get_response(), int (+14 more)

### Community 12 - "Claude Hooks Configuration"
Cohesion: 0.10
Nodes (10): .claude/settings.json (hook registration), deny(), main(), output, _rtk_audit_log(), format-on-save.sh script, graphify-remind.sh script, protect-files.sh script (+2 more)

### Community 13 - "Rebook Promo Tests"
Cohesion: 0.15
Nodes (18): Exception, int, str, handle_callback(): rp_dismiss записує rebook_promo_dismissed_record_id; чужий ca, test_db_failure_on_dismiss_shows_retry_message(), test_dismiss_marks_client(), test_foreign_record_rejected(), _update() (+10 more)

### Community 14 - "Altegio Truth and History Concepts"
Cohesion: 0.16
Nodes (18): db/schema.sql (Supabase schema), Live Altegio Context Injected into Prompt, Altegio as Single Source of Truth, Bot as Telegram Interface to Altegio, AI Chat History Moved to chat_messages Table, Groq Function Calling over Altegio, History Pagination Five Visits Per Page, History Cached in user_data to Limit Altegio Calls (+10 more)

### Community 15 - "Booking Redesign and Management Concepts"
Cohesion: 0.23
Nodes (16): 24-Hour Reschedule/Cancel Rule, booking_incomplete Admin Alert, Breed-Based Service Matching, Mr.Snoopy Grooming Bot Development Roadmap, Redesign to External Altegio Booking Widget, Generic Weight-Based Fallback and Full Price List, Help Phone as Plain Text (tel: URLs Rejected), Phase 11 — Nearest Slots for a Specific Groomer (+8 more)

### Community 16 - "Notification Scheduler Dispatch"
Cohesion: 0.18
Nodes (15): _clear_booking_state(), get_due_notifications(), _handle_booking_incomplete(), _handle_form_incomplete(), _handle_reminder_2h(), int, str, Диспетчер запланованих сповіщень. Викликається cron-ендпоінтом.  Реальна відправ (+7 more)

### Community 17 - "Admin Alerts and Error Handling"
Cohesion: 0.16
Nodes (13): ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, handle_error(), DEFAULT_TYPE, Глобальний обробник помилок PTB.  Без нього виняток, що вилетів з будь-якого han, object, Dual retry policy: interactive (flat, fast) vs background (exponential, patient), notify_admins() (+5 more)

### Community 18 - "Free-Slot Rebook Promo"
Cohesion: 0.18
Nodes (13): get_active_tracked_records_with_ends_at(), Активні записи з відомим ends_at (перевірка прострочених rebook, Фаза 7).      Б, clients.rebook_promo_dismissed_record_id column, last_promo_at cooldown as anti-spam pacing, _latest_per_client(), bool, Фаза 7, п.3: "Маємо вікно завтра" — щоденна перевірка вільних місць для клієнтів, Повертає True лише якщо жодна філія/клієнт не впали з помилкою (той самий     ко (+5 more)

### Community 19 - "Daily Automation Concepts"
Cohesion: 0.21
Nodes (13): Daily Task Gating via cron_state, Deferred Next-Visit-in-N-Weeks Estimate, Per-Branch Error Isolation Contract, Pet Birthday Greeting, Phase 10 — Vaccination Dates from Altegio Comments, Phase 7 — Personal Offers and Automation, REBOOK_DEFAULT_WEEKS Fixed Constant, Two-Layer Anti-Spam for Free-Slot Promo (+5 more)

### Community 20 - "Altegio API Access and Risks"
Cohesion: 0.24
Nodes (12): Altegio Business API, Altegio Online Booking API, External Cron Hitting HTTP /cron Endpoint, Zero-Cost Free-Tier Toolchain Budget, Recommended MVP Release: Phases 0-4, Phase 0 — Foundation and Altegio Integration, Risk 1 — Altegio API Access on Salon Tariff, Risk 10 — No Automatic Backups on Supabase Free Tier (+4 more)

### Community 21 - "Claude Settings Permissions"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 22 - "Registration and Handler Concepts"
Cohesion: 0.24
Nodes (11): handlers/setup.py (single handler registration point), Admin Notifications into a Single Group Topic, Client Lookup in Altegio by Phone Across Branches, Callback Data Ownership Check Against Forged Callbacks, Flow State Encoded in callback_data, draft_json Registration Progress Persistence, form_incomplete Admin Alert, Inline Buttons plus ConversationHandler UI Pattern (+3 more)

### Community 23 - "Reconciliation and Loyalty Concepts"
Cohesion: 0.20
Nodes (10): Altegio Webhook Endpoint with Secret in URL, Visit-Happened Attendance Filter, Daily Altegio Reconciliation of Upcoming Records, Altegio Loyalty API with Local Bonus Tables Fallback, Phase 6 — Bonus / Loyalty Program, Risk 7 — Unverified Altegio Webhook Events and Auth, Risk 3 — Loyalty API Availability, Risk — Altegio Webhook Delivery Not Guaranteed (+2 more)

### Community 24 - "Visit Notification Concepts"
Cohesion: 0.29
Nodes (10): Altegio Fixed +03:00 Offset Timezone Bug, Google Maps Review Prompt for Five-Star Ratings, Idempotent Visit Notification (Re)Scheduling, Notification Type Taxonomy, Phase 4 — Automatic Reminders and Ratings, rebook_nudge Return-Visit Nudge, reminder_2h Pre-Visit Reminder, Live Slot Re-Check Before create_record (+2 more)

### Community 25 - "Promo Callback Ownership Checks"
Cohesion: 0.27
Nodes (9): DEFAULT_TYPE, _owning_client (callback ownership check), handle_callback(), IDOR protection for record_id in callback_data, _owning_client(), int, Callback-кнопки на промо вільних місць (rp_dismiss/rp_snooze) — services/rebook_, RebookPromoCallbackTest (+1 more)

### Community 26 - "Pet Birthday Greetings"
Cohesion: 0.22
Nodes (9): get_pets_with_birth_date(), Усі улюбленці з відомою датою народження (щоденна перевірка днів народження, Фаз, bool, Фаза 7, п.1: день народження улюбленця — щоденне привітання (без знижки, поки що, Привітати клієнтів, чий улюбленець народився сьогодні (без урахування року)., send_birthday_greetings(), All-or-nothing cron_state contract for daily tasks, Задачі, що виконуються раз на добу (а не при кожному 10-хвилинному тику).      Д (+1 more)

### Community 27 - "Telegram Retry Tests"
Cohesion: 0.22
Nodes (4): BaseHTTPRequestHandler, _FlakyHandler, Self-check: send_telegram_message() retries transient 503s via the Session-level, RetryTest

### Community 28 - "Improvement Ideas Backlog"
Cohesion: 0.25
Nodes (7): 📍 Кнопки з локаціями салонів, 🔔 Нагадування про запис, 📸 Обробка фото, 📊 Статистика популярних запитань, 💬 Швидкі відповіді (FAQ кнопки), 💡 Ідеї для покращення бота Mr.Snoopy Grooming, 📅 Інтеграція з Google Calendar

### Community 29 - "MCP Server Configuration"
Cohesion: 0.29
Nodes (6): Authorization, mcpServers, supabase, headers, type, url

### Community 31 - "Graphify Query Memory"
Cohesion: 0.50
Nodes (3): Answer, Q: Чому register_handlers() з'єднує Bot Entrypoints & Handler Setup з 10 іншими спільнотами?, Source Nodes

### Community 32 - "Thanks Rating Handler"
Cohesion: 0.50
Nodes (4): get_client_by_id(), Знайти клієнта за внутрішнім id., _handle_thanks_rating(), Подякувати клієнту через 45 хв після завершення візиту і запитати оцінку послуги

## Ambiguous Edges - Review These
- `start()` → `Query memory: why register_handlers connects Bot Entrypoints community to 10 others`  [AMBIGUOUS]
  graphify-out/memory/query_20260730_135404_чому_register_handlers___з_єднує_bot_entrypoints.md · relation: references
- `_handle_rebook_nudge()` → `clients.rebook_promo_dismissed_record_id column`  [AMBIGUOUS]
  db/migrations/008_phase7_rebook_promo.sql · relation: conceptually_related_to
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to
- `Pet Birthday Greeting` → `Deferred Next-Visit-in-N-Weeks Estimate`  [AMBIGUOUS]
  PLAN.md · relation: semantically_similar_to

## Knowledge Gaps
- **153 isolated node(s):** `type`, `url`, `Authorization`, `str`, `int` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `start()` and `Query memory: why register_handlers connects Bot Entrypoints community to 10 others`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `_handle_rebook_nudge()` and `clients.rebook_promo_dismissed_record_id column`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Pet Birthday Greeting` and `Deferred Next-Visit-in-N-Weeks Estimate`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `with_retry()` connect `Booking and Price Flow` to `Visit History and Shared Validators`, `Supabase Data Access Layer`, `Client Registration Flow`, `Breed-Based Service Matching`, `Pet Card Management`, `Admin Alerts and Error Handling`, `Promo Callback Ownership Checks`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Visit History and Shared Validators` to `Booking and Price Flow`, `Slot Selection and Record Upsert`, `Client Registration Flow`, `Breed-Based Service Matching`, `Pet Card Management`, `Rebook Promo Tests`, `Free-Slot Rebook Promo`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `register_handlers()` connect `Bot Entrypoints and Webhooks` to `Visit History and Shared Validators`, `Promo Callback Ownership Checks`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._