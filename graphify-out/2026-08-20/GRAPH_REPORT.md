# Graph Report - grooming-telegram-bot  (2026-08-20)

## Corpus Check
- 82 files · ~54,873 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1257 nodes · 2636 edges · 89 communities (55 shown, 34 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 139 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7b2de44f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Graphify Query Memory|Graphify Query Memory]]
- [[_COMMUNITY_Thanks Rating Handler|Thanks Rating Handler]]
- [[_COMMUNITY_Local Claude Settings|Local Claude Settings]]
- [[_COMMUNITY_Tracked Records Table|Tracked Records Table]]
- [[_COMMUNITY_Supabase MCP Config|Supabase MCP Config]]
- [[_COMMUNITY_Clients Table|Clients Table]]
- [[_COMMUNITY_Community 39|Community 39]]
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
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Editable Pet Fields|Editable Pet Fields]]
- [[_COMMUNITY_My Bookings Entry|My Bookings Entry]]
- [[_COMMUNITY_Main Menu Keyboard|Main Menu Keyboard]]
- [[_COMMUNITY_My Pets Entry|My Pets Entry]]
- [[_COMMUNITY_Pet Edit Conversation|Pet Edit Conversation]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 83 edges
2. `with_retry()` - 76 edges
3. `AltegioError` - 64 edges
4. `datetime` - 38 edges
5. `InlineKeyboardButton` - 35 edges
6. `show_menu_button()` - 30 edges
7. `process_record()` - 27 edges
8. `Update` - 25 edges
9. `int` - 25 edges
10. `DEFAULT_TYPE` - 24 edges

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

## Communities (89 total, 34 thin omitted)

### Community 0 - "Booking and Price Flow"
Cohesion: 0.10
Nodes (70): _ask_service(), book_start() — «📅 Записатись», _confirm_booking(), format_price(), location_name(), match_services_by_breed(), price_start() — «💰 Дізнатись вартість», registered_client_pets() (+62 more)

### Community 1 - "Visit History and Shared Validators"
Cohesion: 0.07
Nodes (39): _format_visit(), handle_callback(), DEFAULT_TYPE, int, str, Update, Історія візитів («✂️ Історія», Фаза 5): минулі візити клієнта з Altegio.  Читанн, Кнопка меню «✂️ Історія». (+31 more)

### Community 2 - "Supabase Data Access Layer"
Cohesion: 0.05
Nodes (35): code:python ("""send_telegram_document(): файл іде в sendDocument як mult), code:block10 (BACKUP_CHAT_ID=651807767), code:python (import json), code:python (BACKUP_HOUR = 7  # Київ; не збігається з 9 і 10, коли cron ш), code:python (def saturday_of_week(day: date) -> date:), code:bash (git add config.py services/backup.py services/test_backup.py), code:python (class SchedulerWiringTest(unittest.TestCase):), code:python (from services import altegio_reconcile, backup, birthday, no) (+27 more)

### Community 3 - "Bot Entrypoints and Webhooks"
Cohesion: 0.10
Nodes (34): Application, main(), Запуск бота (polling, для локальної розробки)., altegio_webhook_route(), cron(), ensure_initialized(), ensure_initialized_with_retries(), index() (+26 more)

### Community 4 - "Slot Selection and Record Upsert"
Cohesion: 0.07
Nodes (60): resolve_altegio_client_id(), create_client_record(), Створити порожній запис клієнта (реєстрацію заповнюємо покроково)., booking._ask_date, booking._ask_time, booking._confirm_booking, Знайти або створити Altegio-клієнта для обраної локації.      clients.altegio_co, my_bookings._ask_reschedule_date (+52 more)

### Community 5 - "Webhook Reconciliation and Cancellation"
Cohesion: 0.14
Nodes (24): normalize_phone(), get_client_by_phone(), Створити або оновити кеш запису (fields повинні містити altegio_record_id)., Знайти клієнта за телефоном (формат +380XXXXXXXXX). Для матчингу Altegio-вебхукі, upsert_tracked_record(), normalize_phone(), Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на українс, Migration 007: visit notifications (ends_at + altegio_record_id FK) (+16 more)

### Community 6 - "Client Registration Flow"
Cohesion: 0.09
Nodes (71): parse_weight(), with_retry(), Оновити поля клієнта., update_client(), DEFAULT_TYPE, hide_menu_button(), parse_weight(), float (+63 more)

### Community 7 - "Breed-Based Service Matching"
Cohesion: 0.11
Nodes (50): generic_breed_services(), _ask_location(), _ask_service(), _ask_staff(), _breed_eligible_levels(), _category_level(), _confirm(), handle_callback() (+42 more)

### Community 8 - "Pet Card Management"
Cohesion: 0.09
Nodes (45): parse_date(), get_clients_with_altegio_link(), Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)., parse_date(), bool, date, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні., _card_keyboard() (+37 more)

### Community 9 - "Deployment and Webhook Setup"
Cohesion: 0.06
Nodes (38): 1. Завантажити зміни на GitHub (на Mac), 1. Напиши боту в Telegram, 2. Оновити код на PythonAnywhere, 2. Перевір webhook статус, 3. Зупинити старий polling бот (якщо працює), 3. Подивись логи Flask, 4. Налаштувати Web App на PythonAnywhere, 5. Налаштувати WSGI файл (+30 more)

### Community 10 - "Plan Architecture Sections"
Cohesion: 0.06
Nodes (33): 0. Поточний стан і ключове рішення, Altegio API — що використовуємо, code:block1 (grooming-telegram-bot/), code:block2 (clients        id, tg_user_id (unique), altegio_client_id, p), code:block3 (Фаза 0 ✅ (фундамент + Altegio API + вебхуки)), Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint, UI бота: Inline-кнопки + ConversationHandler, Архітектурні рішення (+25 more)

### Community 11 - "AI Chat Assistant"
Cohesion: 0.12
Nodes (25): clear_chat_history(), get_response(), Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., chat_histories (in-memory per-user dict), clear_chat_history(), get_response(), int (+17 more)

### Community 12 - "Claude Hooks Configuration"
Cohesion: 0.08
Nodes (15): .claude/settings.json (hook registration), deny(), find_project_root(), find_project_root(), deny(), main(), output, _rtk_audit_log() (+7 more)

### Community 13 - "Rebook Promo Tests"
Cohesion: 0.13
Nodes (20): Exception, IDOR protection for record_id in callback_data, int, str, handle_callback(): rp_dismiss записує rebook_promo_dismissed_record_id; чужий ca, RebookPromoCallbackTest, test_db_failure_on_dismiss_shows_retry_message(), test_dismiss_marks_client() (+12 more)

### Community 14 - "Altegio Truth and History Concepts"
Cohesion: 0.16
Nodes (18): db/schema.sql (Supabase schema), Live Altegio Context Injected into Prompt, Altegio as Single Source of Truth, Bot as Telegram Interface to Altegio, AI Chat History Moved to chat_messages Table, Groq Function Calling over Altegio, History Pagination Five Visits Per Page, History Cached in user_data to Limit Altegio Calls (+10 more)

### Community 15 - "Booking Redesign and Management Concepts"
Cohesion: 0.23
Nodes (16): 24-Hour Reschedule/Cancel Rule, booking_incomplete Admin Alert, Breed-Based Service Matching, Mr.Snoopy Grooming Bot Development Roadmap, Redesign to External Altegio Booking Widget, Generic Weight-Based Fallback and Full Price List, Help Phone as Plain Text (tel: URLs Rejected), Phase 11 — Nearest Slots for a Specific Groomer (+8 more)

### Community 16 - "Notification Scheduler Dispatch"
Cohesion: 0.06
Nodes (34): 1. Keyset-пагінація замість offset (Important), 2. Прибрано мертвий логер (Important), 3. Комент біля `PAGE_SIZE` (Minor), 4. Запінено склад таблиць і формат `created_at` (Minor), code:block1 (test_backup (unittest.loader._FailedTest.test_backup) ... ER), code:block2 (test_dump_contains_every_table_and_counts ... ok), code:block3 (test_dump_contains_every_table_and_counts ... ok), code:python (batch = page.data or []       # було: rows.extend(batch)) (+26 more)

### Community 17 - "Admin Alerts and Error Handling"
Cohesion: 0.11
Nodes (43): to_kyiv_iso(), get_last_past_tracked_record(), Останній минулий (не скасований) запис клієнта — для «Повторити останній запис»., format_date_label(), kyiv_datetime(), parse_iso_datetime(), datetime, str (+35 more)

### Community 18 - "Free-Slot Rebook Promo"
Cohesion: 0.15
Nodes (18): main() (polling entrypoint), check_webhook(), get_webhook_info(), Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli, set_webhook(), Python dependencies list (+10 more)

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
Cohesion: 0.14
Nodes (18): get_client_by_id(), get_client_by_tg_id(), get_pets_with_birth_date(), get_tracked_record(), Знайти клієнта за Telegram user_id. Повертає None, якщо не знайдено., Знайти клієнта за внутрішнім id., Усі улюбленці з відомою датою народження (щоденна перевірка днів народження, Фаз, Кешований запис за id з Altegio. None, якщо ще не синхронізований. (+10 more)

### Community 23 - "Reconciliation and Loyalty Concepts"
Cohesion: 0.20
Nodes (10): Altegio Webhook Endpoint with Secret in URL, Visit-Happened Attendance Filter, Daily Altegio Reconciliation of Upcoming Records, Altegio Loyalty API with Local Bonus Tables Fallback, Phase 6 — Bonus / Loyalty Program, Risk 7 — Unverified Altegio Webhook Events and Auth, Risk 3 — Loyalty API Availability, Risk — Altegio Webhook Delivery Not Guaranteed (+2 more)

### Community 24 - "Visit Notification Concepts"
Cohesion: 0.29
Nodes (10): Altegio Fixed +03:00 Offset Timezone Bug, Google Maps Review Prompt for Five-Star Ratings, Idempotent Visit Notification (Re)Scheduling, Notification Type Taxonomy, Phase 4 — Automatic Reminders and Ratings, rebook_nudge Return-Visit Nudge, reminder_2h Pre-Visit Reminder, Live Slot Re-Check Before create_record (+2 more)

### Community 25 - "Promo Callback Ownership Checks"
Cohesion: 0.14
Nodes (20): _clear_booking_state(), get_due_notifications(), _handle_booking_incomplete(), _handle_form_incomplete(), _handle_rebook_nudge(), _handle_reminder_2h(), int, str (+12 more)

### Community 27 - "Telegram Retry Tests"
Cohesion: 0.12
Nodes (15): code:block1 (Ran 18 tests in 0.009s), code:block2 (test_due_again_next_week ... ok), `config.py`, `.env` (локально, у git не потрапляє — `.gitignore:2 *.env`), GREEN (після реалізації), RED (до реалізації), `services/backup.py`, Task 3: Тижневе гейтування і відправка дампа — звіт (+7 more)

### Community 28 - "Improvement Ideas Backlog"
Cohesion: 0.25
Nodes (7): 📍 Кнопки з локаціями салонів, 🔔 Нагадування про запис, 📸 Обробка фото, 📊 Статистика популярних запитань, 💬 Швидкі відповіді (FAQ кнопки), 💡 Ідеї для покращення бота Mr.Snoopy Grooming, 📅 Інтеграція з Google Calendar

### Community 29 - "MCP Server Configuration"
Cohesion: 0.29
Nodes (6): Authorization, mcpServers, supabase, headers, type, url

### Community 30 - "Community 30"
Cohesion: 0.14
Nodes (13): code:json ({), Коли запускається, Критерії успіху, Куди надсилається, Обробка помилок, Обсяг дампа, Проблема, Рішення (+5 more)

### Community 31 - "Graphify Query Memory"
Cohesion: 0.50
Nodes (3): Answer, Q: Чому register_handlers() з'єднує Bot Entrypoints & Handler Setup з 10 іншими спільнотами?, Source Nodes

### Community 32 - "Thanks Rating Handler"
Cohesion: 0.10
Nodes (25): bool, create_notification(), delete_pending_notifications_for_record(), get_active_tracked_records_in_range(), get_cron_last_run(), has_pending_notification(), has_tracked_record_since(), mark_notification() (+17 more)

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (7): handle_callback(), _owns_record(), bool, DEFAULT_TYPE, int, Update, callback_data приходить від клієнта Telegram і може бути підроблена     (кастомн

### Community 54 - "Groq API Key"
Cohesion: 0.24
Nodes (11): handlers/setup.py (single handler registration point), Admin Notifications into a Single Group Topic, Client Lookup in Altegio by Phone Across Branches, Callback Data Ownership Check Against Forged Callbacks, Flow State Encoded in callback_data, draft_json Registration Progress Persistence, form_incomplete Admin Alert, Inline Buttons plus ConversationHandler UI Pattern (+3 more)

### Community 55 - "Altegio Partner Token"
Cohesion: 0.13
Nodes (14): 1. Стійкий збій ретраївся на кожному тику (головне), 2. Незаданий `BACKUP_CHAT_ID` — тихий провал, 3. Підпис викидав таблиці з нулем рядків, 4. Дві дрібниці, code:block1 (Ran 28 tests in 0.073s), code:block2 (ERROR: test_not_due_twice_in_same_day_after_failed_attempt), code:block3 (Ran 28 tests in 0.075s), code:block4 (Ran 55 tests in 1.720s) (+6 more)

### Community 64 - "Community 64"
Cohesion: 0.12
Nodes (23): create_pet(), create_rating(), delete_pet(), get_active_tracked_records_with_ends_at(), get_pet(), get_pets_by_client(), get_rating(), get_tracked_record_by_id() (+15 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (13): code:block2 (Content-Type: multipart/form-data), code:block3 (test_caption_omitted_when_not_given ... ERROR), code:block4 (test_caption_omitted_when_not_given ... ok), GREEN (після реалізації), RED (до реалізації), Task 1: Транспорт файла до Telegram — звіт, TDD Evidence, Додаткова перевірка поза тестами (одноразовий скрипт, не комітився) (+5 more)

### Community 67 - "Community 67"
Cohesion: 0.05
Nodes (44): date, datetime, build_dump(), _fetch_table(), is_backup_due(), bool, date, datetime (+36 more)

### Community 71 - "Community 71"
Cohesion: 0.10
Nodes (27): bytes, handle_error(), DEFAULT_TYPE, Глобальний обробник помилок PTB.  Без нього виняток, що вилетів з будь-якого han, object, Dual retry policy: interactive (flat, fast) vs background (exponential, patient), notify_admins(), notify_admins_async() (+19 more)

### Community 74 - "Community 74"
Cohesion: 0.29
Nodes (6): code:block1 (### Відповідність вимогам), Калібрування, Навмисні рішення, які не можна «виправляти», Формат звіту, Що шукати, крім цього, Як дивитись на зміни

### Community 76 - "Community 76"
Cohesion: 0.14
Nodes (13): code:block1 (venv/bin/python -m unittest services.test_backup -v), code:block2 (venv/bin/python -m unittest services.test_backup.SchedulerWi), code:block3 (venv/bin/python -m unittest services.test_backup -v), GREEN (після реалізації), RED (до реалізації, лише тести в `test_backup.py`), Task 4: Підключення до cron-диспетчера — звіт, TDD Evidence, Змінені файли (+5 more)

### Community 79 - "Community 79"
Cohesion: 0.15
Nodes (11): code:markdown (| `services/backup.py` | Тижневий дамп усіх таблиць Supabase), code:bash (git push -u origin feature/supabase-weekly-backup), code:block3 (BACKUP_CHAT_ID=... # особистий чат власника для тижневого бе), code:markdown (- Після додавання нової таблиці в схему: внести її в `BACKUP), code:markdown (| 10 | Бекапи | На free tier Supabase немає автоматичних бек), code:markdown (| 10 | Бекапи | ✅ Закрито 2026-08-18: `services/backup.py` щ), code:bash (git add CLAUDE.md PLAN.md), code:bash (cd ~/MRS_elegram_bot && python3 -c "from services import bac) (+3 more)

### Community 80 - "Community 80"
Cohesion: 0.17
Nodes (10): code:markdown (| `services/backup.py` | Тижневий дамп усіх таблиць Supabase), code:block3 (BACKUP_CHAT_ID=...            # особистий чат власника для т), code:markdown (- Після додавання нової таблиці в схему: внести її в `BACKUP), code:markdown (| 10 | Бекапи | ✅ Закрито 2026-08-18: `services/backup.py` щ), Task 5 — звіт: документація тижневого бекапу (Steps 1–3), Знахідки самоперевірки, Проблеми і сумніви, Розходження брифа з реальністю і як вирішено (+2 more)

### Community 82 - "Community 82"
Cohesion: 0.20
Nodes (9): code:python (class BackupDueTest(unittest.TestCase):), code:python (from datetime import date, datetime), code:python (# Куди слати тижневий бекап Supabase. Особистий чат власника), code:block4 (BACKUP_CHAT_ID=651807767), code:python (import json), code:python (BACKUP_HOUR = 7  # Київ; не збігається з 9 і 10, коли cron ш), code:python (def saturday_of_week(day: date) -> date:), code:bash (git add config.py services/backup.py services/test_backup.py) (+1 more)

### Community 83 - "Community 83"
Cohesion: 0.10
Nodes (19): AI-консультант на живих даних салону + захист від ін'єкцій, Видимість спрацювань, Вичерпана квота Groq, Вміст контексту, Головний інваріант: у промпт не потрапляє текст, написаний клієнтом, Дайджест постраждалих клієнтів о 18:30, Деградація, Детерміновані перевірки відповіді (+11 more)

### Community 84 - "Community 84"
Cohesion: 0.33
Nodes (5): Minor-знахідки (передати фінальному рев'ю), Задачі, Перевірки контролера, Прогрес: тижневий бекап Supabase, Свідомі відступи від тексту плану в Task 2 (спека старша за план)

### Community 85 - "Community 85"
Cohesion: 0.33
Nodes (5): code:python (class SchedulerWiringTest(unittest.TestCase):), code:python (from services import altegio_reconcile, backup, birthday, no), code:python (# Єдина задача не з добовою, а з тижневою каденцією, тому вл), code:bash (git add services/scheduler.py services/test_backup.py), Task 4: Підключення до cron-диспетчера

### Community 86 - "Community 86"
Cohesion: 0.12
Nodes (13): Позначити статус запису (напр. cancelled при скасуванні в Altegio)., update_tracked_record_status(), my_bookings._do_cancel, bool, Щоденна звірка записів Altegio з локальним кешем tracked_records.  Вебхуки (serv, Пройтись по всіх філіях і звірити записи на найближчі RECONCILE_WINDOW_DAYS днів, reconcile_upcoming_records(), Single idempotent record-ingest path for webhook and reconcile (+5 more)

### Community 87 - "Community 87"
Cohesion: 0.40
Nodes (3): code:python ("""send_telegram_document(): файл іде в sendDocument як mult), code:bash (git add services/notifications.py services/test_notification), Task 1: Транспорт файла до Telegram

### Community 88 - "Community 88"
Cohesion: 0.40
Nodes (4): code:python ("""build_dump(): усі таблиці в дампі, великі таблиці читають), code:python ("""Тижневий бекап Supabase: повний дамп таблиць одним JSON-ф), code:bash (git add services/backup.py services/test_backup.py), Task 2: Збірка дампа з Supabase

### Community 89 - "Community 89"
Cohesion: 0.31
Nodes (8): _kyiv_label(), ProcessRecordTest, datetime, str, process_record(): підтвердження клієнту (не слати на вже скасований запис) і час, test_new_active_record_sends_confirmation(), test_new_cancelled_record_sends_no_confirmation(), test_winter_record_keeps_salon_wall_clock_time()

### Community 90 - "Community 90"
Cohesion: 0.22
Nodes (4): BaseHTTPRequestHandler, _FlakyHandler, Self-check: send_telegram_message() retries transient 503s via the Session-level, RetryTest

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
- **294 isolated node(s):** `Проблема`, `Обсяг`, `Рішення`, `Головний інваріант: у промпт не потрапляє текст, написаний клієнтом`, `Модулі` (+289 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

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
- **Why does `datetime` connect `Community 67` to `Community 64`, `Booking and Price Flow`, `Visit History and Shared Validators`, `Webhook Reconciliation and Cancellation`, `Breed-Based Service Matching`, `Pet Card Management`, `Community 71`, `Rebook Promo Tests`, `Admin Alerts and Error Handling`, `Community 86`, `Promo Callback Ownership Checks`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Breed-Based Service Matching` to `Booking and Price Flow`, `Visit History and Shared Validators`, `Community 67`, `Slot Selection and Record Upsert`, `Client Registration Flow`, `Pet Card Management`, `Rebook Promo Tests`, `Admin Alerts and Error Handling`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `with_retry()` connect `Client Registration Flow` to `Booking and Price Flow`, `Visit History and Shared Validators`, `Community 39`, `Pet Card Management`, `Breed-Based Service Matching`, `Community 71`, `Admin Alerts and Error Handling`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._