# Graph Report - grooming-telegram-bot  (2026-07-27)

## Corpus Check
- 42 files · ~22,543 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 589 nodes · 1211 edges · 47 communities (24 shown, 23 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 56 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7158577e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Supabase Client CRUD|Supabase Client CRUD]]
- [[_COMMUNITY_Booking Flow (ДатаЧасКатегорія)|Booking Flow (Дата/Час/Категорія)]]
- [[_COMMUNITY_Bot Entry Points & Setup|Bot Entry Points & Setup]]
- [[_COMMUNITY_Cron & Admin Utilities|Cron & Admin Utilities]]
- [[_COMMUNITY_Pet Registration Flow|Pet Registration Flow]]
- [[_COMMUNITY_Error Handling & Handler Setup|Error Handling & Handler Setup]]
- [[_COMMUNITY_Reschedule & Cancel Flow|Reschedule & Cancel Flow]]
- [[_COMMUNITY_Deployment Guide|Deployment Guide]]
- [[_COMMUNITY_Altegio API Client|Altegio API Client]]
- [[_COMMUNITY_Project Plan & Architecture|Project Plan & Architecture]]
- [[_COMMUNITY_Pet Card UI|Pet Card UI]]
- [[_COMMUNITY_Groq AI Chat|Groq AI Chat]]
- [[_COMMUNITY_Claude Code Hooks|Claude Code Hooks]]
- [[_COMMUNITY_Vaccine Reminder Sync|Vaccine Reminder Sync]]
- [[_COMMUNITY_Hook Permissions Config|Hook Permissions Config]]
- [[_COMMUNITY_Feature Ideas Backlog|Feature Ideas Backlog]]
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
- [[_COMMUNITY_Calendar Integration Idea|Calendar Integration Idea]]
- [[_COMMUNITY_Location Buttons Idea|Location Buttons Idea]]
- [[_COMMUNITY_FAQ Quick-Reply Idea|FAQ Quick-Reply Idea]]
- [[_COMMUNITY_Popular Questions Stats Idea|Popular Questions Stats Idea]]
- [[_COMMUNITY_Reminder Notifications Idea|Reminder Notifications Idea]]
- [[_COMMUNITY_Groq API Key Config|Groq API Key Config]]
- [[_COMMUNITY_Altegio Partner Token Config|Altegio Partner Token Config]]
- [[_COMMUNITY_Altegio User Token Config|Altegio User Token Config]]
- [[_COMMUNITY_Supabase URL Config|Supabase URL Config]]
- [[_COMMUNITY_Supabase Key Config|Supabase Key Config]]
- [[_COMMUNITY_Editable Pet Fields Config|Editable Pet Fields Config]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 50 edges
2. `AltegioError` - 35 edges
3. `InlineKeyboardButton` - 23 edges
4. `int` - 21 edges
5. `handle_callback()` - 20 edges
6. `register_handlers()` - 20 edges
7. `Update` - 19 edges
8. `int` - 19 edges
9. `DEFAULT_TYPE` - 18 edges
10. `handle_callback()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `_location_name()` --semantically_similar_to--> `_location_name()`  [INFERRED] [semantically similar]
  handlers/booking.py → services/altegio_webhook.py
- `with_retry()` --semantically_similar_to--> `send_telegram_message()`  [INFERRED] [semantically similar]
  handlers/common.py → services/notifications.py
- `str` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py
- `bool` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py
- `bool` --uses--> `AltegioError`  [INFERRED]
  handlers/booking.py → services/altegio.py

## Hyperedges (group relationships)
- **tracked_records створюються/оновлюються (бот або Altegio-вебхук) і синхронно планують reminder_2h/thanks_rating** — handlers_booking_confirm_booking, handlers_my_bookings_confirm_reschedule, services_altegio_webhook_handle, services_notifications_schedule_visit_notifications, db_client_upsert_tracked_record [INFERRED 0.85]
- **Щоденний конвеєр: коментар Altegio → vaccine_due_date/vaccine_notified_due_date → нагадування о 7 днях** — services_vaccine_sync_sync_vaccine_dates, migrations_004_phase10_vaccine_due_date_vaccine_due_date_column, migrations_005_phase10_vaccine_notified_flag_notified_column, services_scheduler_run_daily_tasks [INFERRED 0.85]
- **Флоу оцінки після візиту: thanks_rating → inline ⭐ → ratings → низька оцінка адмінам / 5+5 Google Maps** — services_scheduler_handle_thanks_rating, handlers_rating_handle_callback, db_client_create_rating, config_google_maps_review_urls [INFERRED 0.85]

## Communities (47 total, 23 thin omitted)

### Community 0 - "Supabase Client CRUD"
Cohesion: 0.12
Nodes (25): create_pet(), create_rating(), delete_pet(), get_client_by_tg_id(), get_last_past_tracked_record(), get_pet(), get_pets_by_client(), get_tracked_record() (+17 more)

### Community 1 - "Booking Flow (Дата/Час/Категорія)"
Cohesion: 0.12
Nodes (48): _ask_category(), _ask_date(), _ask_location(), _ask_service(), _ask_time(), book_start(), _category_keyboard(), _category_type_key() (+40 more)

### Community 2 - "Bot Entry Points & Setup"
Cohesion: 0.09
Nodes (33): Application, main(), Запуск бота (polling, для локальної розробки)., altegio_webhook_route(), cron(), ensure_initialized(), ensure_initialized_with_retries(), index() (+25 more)

### Community 3 - "Cron & Admin Utilities"
Cohesion: 0.13
Nodes (23): CRON_SECRET, get_client_by_id(), Знайти клієнта за внутрішнім id., Фаза 4 — Автоматичні нагадування + оцінки, _clear_booking_state(), get_due_notifications(), _handle_booking_incomplete(), _handle_form_incomplete() (+15 more)

### Community 4 - "Pet Registration Flow"
Cohesion: 0.14
Nodes (43): parse_weight(), float, int, Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, Викликати Telegram-запит (reply_text/reply_location/...) з повторами.      Прокс, with_retry(), add_pet_start(), _ask_location() (+35 more)

### Community 5 - "Error Handling & Handler Setup"
Cohesion: 0.10
Nodes (27): ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, create_notification(), Запланувати сповіщення (send_after — ISO timestamp)., handle_error(), DEFAULT_TYPE, Глобальний обробник помилок PTB.  Без нього виняток, що вилетів з будь-якого han, notifications.altegio_record_id column (+19 more)

### Community 6 - "Reschedule & Cancel Flow"
Cohesion: 0.14
Nodes (33): datetime, kyiv_datetime(), normalize_phone(), parse_iso_datetime(), str, Спільні валідатори полів анкети та карток улюбленців., Захисний парсинг timestamptz-рядка з Supabase/Altegio (інколи із 'Z' замість off, 2026-08-01', '10:00' -> aware ISO-рядок у Europe/Kyiv, для запису в timestamptz- (+25 more)

### Community 7 - "Deployment Guide"
Cohesion: 0.06
Nodes (38): 1. Завантажити зміни на GitHub (на Mac), 1. Напиши боту в Telegram, 2. Оновити код на PythonAnywhere, 2. Перевір webhook статус, 3. Зупинити старий polling бот (якщо працює), 3. Подивись логи Flask, 4. Налаштувати Web App на PythonAnywhere, 5. Налаштувати WSGI файл (+30 more)

### Community 8 - "Altegio API Client"
Cohesion: 0.12
Nodes (35): create_client_record(), Створити порожній запис клієнта (реєстрацію заповнюємо покроково)., cancel_record(), create_client(), create_record(), find_available_staff_for_slot(), find_client_by_phone(), get_available_dates() (+27 more)

### Community 9 - "Project Plan & Architecture"
Cohesion: 0.06
Nodes (32): 0. Поточний стан і ключове рішення, Altegio API — що використовуємо, code:block1 (grooming-telegram-bot/), code:block2 (clients        id, tg_user_id (unique), altegio_client_id, p), code:block3 (Фаза 0 ✅ (фундамент + Altegio API + вебхуки)), Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint, UI бота: Inline-кнопки + ConversationHandler, Архітектурні рішення (+24 more)

### Community 10 - "Pet Card UI"
Cohesion: 0.20
Nodes (23): _card_keyboard(), _card_text(), _delete_confirm_keyboard(), edit_cancel(), edit_field_start(), edit_field_value(), _edit_keyboard(), _format_date() (+15 more)

### Community 11 - "Groq AI Chat"
Cohesion: 0.13
Nodes (22): SYSTEM_PROMPT, clear_chat_history(), get_response(), Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., chat_histories (in-memory per-user dict), clear_chat_history(), get_response() (+14 more)

### Community 12 - "Claude Code Hooks"
Cohesion: 0.08
Nodes (15): .claude/settings.json (hook registration), deny(), find_project_root(), find_project_root(), deny(), main(), output, _rtk_audit_log() (+7 more)

### Community 13 - "Vaccine Reminder Sync"
Cohesion: 0.10
Nodes (30): date, get_clients_with_altegio_link(), Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)., Exception, parse_date(), bool, date, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні. (+22 more)

### Community 14 - "Hook Permissions Config"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 15 - "Feature Ideas Backlog"
Cohesion: 0.25
Nodes (7): 📍 Кнопки з локаціями салонів, 🔔 Нагадування про запис, 📸 Обробка фото, 📊 Статистика популярних запитань, 💬 Швидкі відповіді (FAQ кнопки), 💡 Ідеї для покращення бота Mr.Snoopy Grooming, 📅 Інтеграція з Google Calendar

### Community 40 - "Community 40"
Cohesion: 0.15
Nodes (19): main() (polling entrypoint), TELEGRAM_TOKEN, check_webhook(), get_webhook_info(), Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli, set_webhook() (+11 more)

### Community 41 - "Community 41"
Cohesion: 0.15
Nodes (20): ALTEGIO_LOCATIONS, HELP_PHONE, Кешований запис за id з Altegio. None, якщо ще не синхронізований., Створити або оновити кеш запису (fields повинні містити altegio_record_id)., upsert_tracked_record(), PLAN.md — план розвитку, Altegio як єдине джерело правди (архітектурний принцип), Фаза 2 — Онлайн-запис через Altegio Online Booking API (+12 more)

### Community 42 - "Community 42"
Cohesion: 0.20
Nodes (11): GOOGLE_MAPS_REVIEW_URLS, get_rating(), Оцінка запису, якщо вже поставлена (захист від подвійного тапу)., handle_callback(), _owns_record(), bool, DEFAULT_TYPE, int (+3 more)

### Community 43 - "Community 43"
Cohesion: 0.33
Nodes (7): get_cron_last_run(), Дата (ISO) останнього запуску щоденної задачі з цим ключем. None, якщо ще не зап, Позначити, що щоденна задача виконана сьогодні (ISO-дата)., set_cron_last_run(), cron_state table, Задачі, що виконуються раз на добу (а не при кожному 10-хвилинному тику).      Д, _run_daily_tasks()

### Community 45 - "Community 45"
Cohesion: 0.15
Nodes (15): bool, delete_pending_notifications_for_record(), get_client_by_phone(), has_pending_notification(), has_tracked_record_since(), mark_notification(), bool, str (+7 more)

## Ambiguous Edges - Review These
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to

## Knowledge Gaps
- **108 isolated node(s):** `allow`, `deny`, `defaultMode`, `enabled`, `PreToolUse` (+103 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `register_handlers()` connect `Bot Entry Points & Setup` to `Booking Flow (Дата/Час/Категорія)`, `Error Handling & Handler Setup`, `Reschedule & Cancel Flow`, `Community 40`, `Pet Card UI`, `Groq AI Chat`, `Community 42`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Vaccine Reminder Sync` to `Altegio API Client`, `Booking Flow (Дата/Час/Категорія)`, `Pet Registration Flow`, `Reschedule & Cancel Flow`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `Фази реалізації` connect `Project Plan & Architecture` to `Cron & Admin Utilities`, `Vaccine Reminder Sync`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `AltegioError` (e.g. with `DEFAULT_TYPE` and `str`) actually correct?**
  _`AltegioError` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `InlineKeyboardButton` (e.g. with `AltegioError` and `show_bookings()`) actually correct?**
  _`InlineKeyboardButton` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Запуск бота (polling, для локальної розробки).`, `Головна сторінка - перевірка що бот працює.`, `Обробник webhook від Telegram.` to the rest of the system?**
  _209 weakly-connected nodes found - possible documentation gaps or missing edges._