# Graph Report - grooming-telegram-bot  (2026-08-04)

## Corpus Check
- 53 files · ~29,667 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 688 nodes · 1520 edges · 57 communities (31 shown, 26 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eaef3a0f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Common DatePhone Helpers + My Bookings|Common Date/Phone Helpers + My Bookings]]
- [[_COMMUNITY_Booking Flow — CategoryService Selection|Booking Flow — Category/Service Selection]]
- [[_COMMUNITY_Altegio API Client + Booking Confirm|Altegio API Client + Booking Confirm]]
- [[_COMMUNITY_Nearest Slots Flow|Nearest Slots Flow]]
- [[_COMMUNITY_Client Registration Flow|Client Registration Flow]]
- [[_COMMUNITY_Webhook Setup Doc|Webhook Setup Doc]]
- [[_COMMUNITY_Pet Cards + Altegio Comment Sync|Pet Cards + Altegio Comment Sync]]
- [[_COMMUNITY_PLAN.md — Roadmap|PLAN.md — Roadmap]]
- [[_COMMUNITY_Notification Scheduler|Notification Scheduler]]
- [[_COMMUNITY_DB Client — PetsRatingsNotifications|DB Client — Pets/Ratings/Notifications]]
- [[_COMMUNITY_Webhook Bot Entrypoint (Flask)|Webhook Bot Entrypoint (Flask)]]
- [[_COMMUNITY_Claude Hooks|Claude Hooks]]
- [[_COMMUNITY_AI Chat (Groq) + Menu|AI Chat (Groq) + Menu]]
- [[_COMMUNITY_Booking Entry Points + Widget Redesign|Booking Entry Points + Widget Redesign]]
- [[_COMMUNITY_Notification SchedulingCancellation|Notification Scheduling/Cancellation]]
- [[_COMMUNITY_Bot Setup — Handler Registration|Bot Setup — Handler Registration]]
- [[_COMMUNITY_Altegio Webhook Handler|Altegio Webhook Handler]]
- [[_COMMUNITY_Retry Policy + Admin Notify|Retry Policy + Admin Notify]]
- [[_COMMUNITY_Rating Flow|Rating Flow]]
- [[_COMMUNITY_Claude Settings — Hooks Config|Claude Settings — Hooks Config]]
- [[_COMMUNITY_set_webhook.py|set_webhook.py]]
- [[_COMMUNITY_DB Client — PhoneDedup Lookups|DB Client — Phone/Dedup Lookups]]
- [[_COMMUNITY_IDOR Ownership Checks|IDOR Ownership Checks]]
- [[_COMMUNITY_Notification Retry Tests|Notification Retry Tests]]
- [[_COMMUNITY_ideas|ideas.md]]
- [[_COMMUNITY_App Entrypoints (bot.pywebhook_bot.pywsgi.py)|App Entrypoints (bot.py/webhook_bot.py/wsgi.py)]]
- [[_COMMUNITY_Daily Cron Tasks (Vaccine)|Daily Cron Tasks (Vaccine)]]
- [[_COMMUNITY_.mcp.json — Supabase MCP|.mcp.json — Supabase MCP]]
- [[_COMMUNITY_Error Handler|Error Handler]]
- [[_COMMUNITY_Graphify Memory — register_handlers Query|Graphify Memory — register_handlers Query]]
- [[_COMMUNITY_Claude Local Settings|Claude Local Settings]]
- [[_COMMUNITY_Claude Local Settings — Enabled MCP|Claude Local Settings — Enabled MCP]]
- [[_COMMUNITY_DB Schema — clients|DB Schema — clients]]
- [[_COMMUNITY_DB Schema — tracked_records|DB Schema — tracked_records]]
- [[_COMMUNITY_Welcome Message|Welcome Message]]
- [[_COMMUNITY_Groq Client|Groq Client]]
- [[_COMMUNITY_DB Schema — pets|DB Schema — pets]]
- [[_COMMUNITY_DB Schema — visit_extras|DB Schema — visit_extras]]
- [[_COMMUNITY_DB Schema — ratings|DB Schema — ratings]]
- [[_COMMUNITY_DB Schema — notifications|DB Schema — notifications]]
- [[_COMMUNITY_DB Schema — chat_messages|DB Schema — chat_messages]]
- [[_COMMUNITY_ideas.md doc node|ideas.md doc node]]
- [[_COMMUNITY_Idea — Photo Consultations|Idea — Photo Consultations]]
- [[_COMMUNITY_Idea — Google Calendar|Idea — Google Calendar]]
- [[_COMMUNITY_Idea — Location Buttons|Idea — Location Buttons]]
- [[_COMMUNITY_Idea — FAQ Quick Replies|Idea — FAQ Quick Replies]]
- [[_COMMUNITY_Idea — Popular Questions Stats|Idea — Popular Questions Stats]]
- [[_COMMUNITY_Idea — Appointment Reminders|Idea — Appointment Reminders]]
- [[_COMMUNITY_Groq API Key|Groq API Key]]
- [[_COMMUNITY_Altegio Partner Token|Altegio Partner Token]]
- [[_COMMUNITY_Altegio User Token|Altegio User Token]]
- [[_COMMUNITY_Supabase URL|Supabase URL]]
- [[_COMMUNITY_Supabase Service Key|Supabase Service Key]]
- [[_COMMUNITY_Pets Editable Fields|Pets Editable Fields]]
- [[_COMMUNITY_Main Menu|Main Menu]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 77 edges
2. `AltegioError` - 42 edges
3. `InlineKeyboardButton` - 35 edges
4. `register_handlers()` - 30 edges
5. `show_menu_button()` - 24 edges
6. `int` - 21 edges
7. `handle_callback()` - 21 edges
8. `Update` - 20 edges
9. `int` - 20 edges
10. `handle_callback()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Query memory: why register_handlers connects Bot Entrypoints community to 10 others` --references--> `start()`  [AMBIGUOUS]
  graphify-out/memory/query_20260730_135404_чому_register_handlers___з_єднує_bot_entrypoints.md → handlers/nearest_slots.py
- `location_name()` --semantically_similar_to--> `_location_name()`  [INFERRED] [semantically similar]
  handlers/booking.py → services/altegio_webhook.py
- `with_retry()` --semantically_similar_to--> `send_telegram_message()`  [INFERRED] [semantically similar]
  handlers/common.py → services/notifications.py
- `str` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py
- `bool` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py

## Hyperedges (group relationships)
- **Any-master -> concrete staff_id resolution at confirmation time** — services_altegio_find_available_staff_for_slot, handlers_booking__confirm_booking, handlers_nearest_slots__confirm, handlers_my_bookings__confirm_reschedule [INFERRED 0.85]
- **In-memory context.user_data flow state shared design across booking/nearest-slots/reschedule/pet-edit** — handlers_booking_price_start, handlers_nearest_slots_start, handlers_my_bookings__confirm_reschedule, handlers_pets_edit_field_start [EXTRACTED 0.90]
- **Two independent retry mechanisms guarding the same PythonAnywhere proxy 502/503/504 issue** — handlers_common_with_retry, services_notifications_send_telegram_message, services_altegio__request [EXTRACTED 0.95]

## Communities (57 total, 26 thin omitted)

### Community 0 - "Common Date/Phone Helpers + My Bookings"
Cohesion: 0.07
Nodes (55): normalize_phone(), to_kyiv_iso(), datetime, format_date_label(), kyiv_datetime(), parse_iso_datetime(), str, Спільні валідатори полів анкети та карток улюбленців. (+47 more)

### Community 1 - "Booking Flow — Category/Service Selection"
Cohesion: 0.12
Nodes (55): _ask_service(), _confirm_booking(), format_price(), generic_breed_services(), location_name(), match_services_by_breed(), slim_service(), staff_name() (+47 more)

### Community 2 - "Altegio API Client + Booking Confirm"
Cohesion: 0.09
Nodes (49): resolve_altegio_client_id(), create_client_record(), Створити порожній запис клієнта (реєстрацію заповнюємо покроково)., Створити або оновити кеш запису (fields повинні містити altegio_record_id)., upsert_tracked_record(), booking._ask_date, booking._ask_time, booking._confirm_booking (+41 more)

### Community 3 - "Nearest Slots Flow"
Cohesion: 0.16
Nodes (35): _ask_location(), _ask_staff(), _breed_eligible_levels(), _category_level(), handle_callback(), _level_of_text(), _location_keyboard(), _pet_keyboard() (+27 more)

### Community 4 - "Client Registration Flow"
Cohesion: 0.10
Nodes (54): parse_weight(), with_retry(), Оновити поля клієнта., update_client(), hide_menu_button(), float, int, Приховати нативну кнопку «Меню» (/start, /cancel) на час активного флоу     (анк (+46 more)

### Community 5 - "Webhook Setup Doc"
Cohesion: 0.06
Nodes (35): 1. Завантажити зміни на GitHub (на Mac), 1. Напиши боту в Telegram, 2. Оновити код на PythonAnywhere, 2. Перевір webhook статус, 3. Зупинити старий polling бот (якщо працює), 3. Подивись логи Flask, 4. Налаштувати Web App на PythonAnywhere, 5. Налаштувати WSGI файл (+27 more)

### Community 6 - "Pet Cards + Altegio Comment Sync"
Cohesion: 0.18
Nodes (25): Показати кнопку «Меню» — клієнт поза флоу (вільний AI-чат чи заглушки меню)., show_menu_button(), _card_keyboard(), _card_text(), _delete_confirm_keyboard(), edit_cancel(), edit_field_start(), _edit_keyboard() (+17 more)

### Community 7 - "PLAN.md — Roadmap"
Cohesion: 0.06
Nodes (32): 0. Поточний стан і ключове рішення, Altegio API — що використовуємо, code:block1 (grooming-telegram-bot/), code:block2 (clients        id, tg_user_id (unique), altegio_client_id, p), code:block3 (Фаза 0 ✅ (фундамент + Altegio API + вебхуки)), Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint, UI бота: Inline-кнопки + ConversationHandler, Архітектурні рішення (+24 more)

### Community 8 - "Notification Scheduler"
Cohesion: 0.09
Nodes (29): parse_date(), date, get_clients_with_altegio_link(), Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)., Exception, bool, bool, date (+21 more)

### Community 9 - "DB Client — Pets/Ratings/Notifications"
Cohesion: 0.17
Nodes (17): create_pet(), delete_pet(), get_last_past_tracked_record(), get_pet(), get_pets_by_client(), get_upcoming_tracked_records(), int, Клієнт Supabase. Всі звернення до локальної БД йдуть через цей модуль. (+9 more)

### Community 10 - "Webhook Bot Entrypoint (Flask)"
Cohesion: 0.15
Nodes (13): CRON_SECRET, cron(), index(), ensure_initialized() з повторами - проксі PythonAnywhere інколи віддає 503., Головна сторінка - перевірка що бот працює., Обробник webhook від Telegram., Викликається зовнішнім планувальником (cron-job.org / PythonAnywhere Scheduled T, webhook() (+5 more)

### Community 11 - "Claude Hooks"
Cohesion: 0.10
Nodes (10): .claude/settings.json (hook registration), deny(), main(), output, _rtk_audit_log(), format-on-save.sh script, graphify-remind.sh script, protect-files.sh script (+2 more)

### Community 12 - "AI Chat (Groq) + Menu"
Cohesion: 0.11
Nodes (21): HELP_PHONE, SYSTEM_PROMPT, Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., chat_histories (in-memory per-user dict), clear_chat_history(), get_response(), int (+13 more)

### Community 13 - "Booking Entry Points + Widget Redesign"
Cohesion: 0.33
Nodes (5): Application, Єдина точка реєстрації всіх handler-ів (webhook_bot.py і bot.py)., Глобальний дефолт кнопки «Меню» (/start, /cancel) для нових чатів.      Під час, Query memory: why register_handlers connects Bot Entrypoints community to 10 others, post_init()

### Community 14 - "Notification Scheduling/Cancellation"
Cohesion: 0.05
Nodes (42): BaseHTTPRequestHandler, ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, handle_error(), DEFAULT_TYPE, Глобальний обробник помилок PTB.  Без нього виняток, що вилетів з будь-якого han, my_bookings._do_cancel, Migration 007: visit notifications (ends_at + altegio_record_id FK) (+34 more)

### Community 15 - "Bot Setup — Handler Registration"
Cohesion: 0.16
Nodes (14): book_start() — «📅 Записатись», price_start() — «💰 Дізнатись вартість», registered_client_pets(), ALTEGIO_BOOKING_WIDGET_URL, main(), Запуск бота (polling, для локальної розробки)., (client, pets), якщо анкета заповнена і є хоча б один улюбленець — інакше None (, pets.edit_conversation (ConversationHandler) (+6 more)

### Community 16 - "Altegio Webhook Handler"
Cohesion: 0.17
Nodes (12): get_client_by_phone(), get_cron_last_run(), mark_notification(), str, Позначити статус запису (напр. cancelled при скасуванні в Altegio)., Позначити сповіщення як sent/failed., Дата (ISO) останнього запуску щоденної задачі з цим ключем. None, якщо ще не зап, Позначити, що щоденна задача виконана сьогодні (ISO-дата). (+4 more)

### Community 17 - "Retry Policy + Admin Notify"
Cohesion: 0.24
Nodes (10): altegio_webhook_route(), Приймає події від Altegio (запис створено/змінено/видалено)., Запустити event loop в окремому потоці., Ініціалізувати Telegram Application., Перевірити чи event loop живий і працює., Переконатись що бот ініціалізований. Перезапускає якщо event loop помер., ensure_initialized(), initialize_application() (+2 more)

### Community 18 - "Rating Flow"
Cohesion: 0.16
Nodes (13): GOOGLE_MAPS_REVIEW_URLS, create_rating(), get_rating(), Записати оцінку послуги/грумера для завершеного візиту., Оцінка запису, якщо вже поставлена (захист від подвійного тапу)., handle_callback(), _owns_record(), bool (+5 more)

### Community 19 - "Claude Settings — Hooks Config"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 20 - "set_webhook.py"
Cohesion: 0.27
Nodes (9): TELEGRAM_TOKEN, Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli, check_webhook(), get_webhook_info(), str, WEBHOOK_URL constant (+1 more)

### Community 21 - "DB Client — Phone/Dedup Lookups"
Cohesion: 0.29
Nodes (8): bool, get_active_tracked_records_in_range(), has_pending_notification(), has_tracked_record_since(), bool, Активні записи філії в межах вікна дат (для щоденної звірки: скасовані в Altegio, Чи з'явився активний запис клієнта після вказаного часу (перевірка, чи флоу запи, Чи є вже заплановане (pending) сповіщення цього типу для клієнта.

### Community 22 - "IDOR Ownership Checks"
Cohesion: 0.19
Nodes (14): get_client_by_id(), get_client_by_tg_id(), get_tracked_record(), get_tracked_record_by_id(), Кешований запис за внутрішнім id (дії клієнта: перенос/скасування)., Знайти клієнта за Telegram user_id. Повертає None, якщо не знайдено., Знайти клієнта за внутрішнім id., Кешований запис за id з Altegio. None, якщо ще не синхронізований. (+6 more)

### Community 23 - "Notification Retry Tests"
Cohesion: 0.25
Nodes (8): create_notification(), delete_pending_notifications_for_record(), Запланувати сповіщення (send_after — ISO timestamp)., Видалити pending-сповіщення заданих типів для конкретного запису (Фаза 4: remind, booking._select_service, notifications.altegio_record_id column, Запланувати перевірку 'клієнт почав запис, але не завершив' на сьогодні 18:00 (К, schedule_booking_incomplete()

### Community 24 - "ideas.md"
Cohesion: 0.25
Nodes (7): 📍 Кнопки з локаціями салонів, 🔔 Нагадування про запис, 📸 Обробка фото, 📊 Статистика популярних запитань, 💬 Швидкі відповіді (FAQ кнопки), 💡 Ідеї для покращення бота Mr.Snoopy Grooming, 📅 Інтеграція з Google Calendar

### Community 25 - "App Entrypoints (bot.py/webhook_bot.py/wsgi.py)"
Cohesion: 0.33
Nodes (7): main() (polling entrypoint), Python dependencies list, python-3.11.0 runtime pin, Flask app instance, WEBHOOK_SETUP.md (deployment guide), Webhook-over-polling rationale (PythonAnywhere free tier blocks polling), application (WSGI entry, binds webhook_bot.app)

### Community 26 - "Daily Cron Tasks (Vaccine)"
Cohesion: 0.47
Nodes (4): ProcessRecordTest, process_record() reconcile path: жоден бренд-новий-і-вже-скасований запис (webho, test_new_active_record_sends_confirmation(), test_new_cancelled_record_sends_no_confirmation()

### Community 27 - ".mcp.json — Supabase MCP"
Cohesion: 0.29
Nodes (6): Authorization, mcpServers, supabase, headers, type, url

### Community 29 - "Graphify Memory — register_handlers Query"
Cohesion: 0.50
Nodes (3): Answer, Q: Чому register_handlers() з'єднує Bot Entrypoints & Handler Setup з 10 іншими спільнотами?, Source Nodes

## Ambiguous Edges - Review These
- `start()` → `Query memory: why register_handlers connects Bot Entrypoints community to 10 others`  [AMBIGUOUS]
  graphify-out/memory/query_20260730_135404_чому_register_handlers___з_єднує_bot_entrypoints.md · relation: references
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to

## Knowledge Gaps
- **133 isolated node(s):** `0. Поточний стан і ключове рішення`, `⚠️ Перевірити на старті (Фаза 0, до написання коду)`, `💸 Бюджет: всі інструменти безоплатні`, `БД: Supabase (безкоштовний tier)`, `Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `start()` and `Query memory: why register_handlers connects Bot Entrypoints community to 10 others`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `register_handlers()` connect `Bot Setup — Handler Registration` to `Common Date/Phone Helpers + My Bookings`, `Booking Flow — Category/Service Selection`, `Nearest Slots Flow`, `Client Registration Flow`, `Pet Cards + Altegio Comment Sync`, `AI Chat (Groq) + Menu`, `Booking Entry Points + Widget Redesign`, `Notification Scheduling/Cancellation`, `Retry Policy + Admin Notify`, `Rating Flow`, `App Entrypoints (bot.py/webhook_bot.py/wsgi.py)`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `with_retry()` connect `Client Registration Flow` to `Common Date/Phone Helpers + My Bookings`, `Booking Flow — Category/Service Selection`, `Nearest Slots Flow`, `Pet Cards + Altegio Comment Sync`, `Notification Scheduling/Cancellation`, `Bot Setup — Handler Registration`, `Rating Flow`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Notification Scheduler` to `Common Date/Phone Helpers + My Bookings`, `Booking Flow — Category/Service Selection`, `Altegio API Client + Booking Confirm`, `Nearest Slots Flow`, `Client Registration Flow`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `AltegioError` (e.g. with `DEFAULT_TYPE` and `str`) actually correct?**
  _`AltegioError` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `InlineKeyboardButton` (e.g. with `handle_callback()` and `show_bookings()`) actually correct?**
  _`InlineKeyboardButton` has 12 INFERRED edges - model-reasoned connections that need verification._