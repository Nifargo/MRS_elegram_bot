# Graph Report - .  (2026-07-24)

## Corpus Check
- 18 files · ~23,653 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 552 nodes · 1124 edges · 40 communities (18 shown, 22 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 54 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 50 edges
2. `AltegioError` - 33 edges
3. `InlineKeyboardButton` - 23 edges
4. `int` - 20 edges
5. `handle_callback()` - 20 edges
6. `Update` - 19 edges
7. `int` - 19 edges
8. `register_handlers()` - 19 edges
9. `DEFAULT_TYPE` - 18 edges
10. `handle_callback()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `_location_name()` --semantically_similar_to--> `_location_name()`  [INFERRED] [semantically similar]
  handlers/booking.py → services/altegio_webhook.py
- `with_retry()` --semantically_similar_to--> `send_telegram_message()`  [INFERRED] [semantically similar]
  handlers/common.py → services/notifications.py
- `Altegio як єдине джерело правди (архітектурний принцип)` --rationale_for--> `upsert_tracked_record()`  [EXTRACTED]
  PLAN.md → db/client.py
- `str` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py
- `bool` --uses--> `AltegioError`  [INFERRED]
  handlers/registration.py → services/altegio.py

## Hyperedges (group relationships)
- **tracked_records створюються/оновлюються (бот або Altegio-вебхук) і синхронно планують reminder_2h/thanks_rating** — handlers_booking_confirm_booking, handlers_my_bookings_confirm_reschedule, services_altegio_webhook_handle, services_notifications_schedule_visit_notifications, db_client_upsert_tracked_record [INFERRED 0.85]
- **Щоденний конвеєр: коментар Altegio → vaccine_due_date/vaccine_notified_due_date → нагадування о 7 днях** — services_vaccine_sync_sync_vaccine_dates, migrations_004_phase10_vaccine_due_date_vaccine_due_date_column, migrations_005_phase10_vaccine_notified_flag_notified_column, services_scheduler_run_daily_tasks [INFERRED 0.85]
- **Флоу оцінки після візиту: thanks_rating → inline ⭐ → ratings → низька оцінка адмінам / 5+5 Google Maps** — services_scheduler_handle_thanks_rating, handlers_rating_handle_callback, db_client_create_rating, config_google_maps_review_urls [INFERRED 0.85]

## Communities (40 total, 22 thin omitted)

### Community 0 - "Supabase Client CRUD"
Cohesion: 0.05
Nodes (57): bool, GOOGLE_MAPS_REVIEW_URLS, create_notification(), create_pet(), create_rating(), delete_pending_notifications_for_record(), delete_pet(), get_client_by_phone() (+49 more)

### Community 1 - "Booking Flow (Дата/Час/Категорія)"
Cohesion: 0.13
Nodes (47): ALTEGIO_LOCATIONS, _ask_category(), _ask_date(), _ask_location(), _ask_service(), _ask_time(), book_start(), _category_keyboard() (+39 more)

### Community 2 - "Bot Entry Points & Setup"
Cohesion: 0.06
Nodes (43): Application, main() (polling entrypoint), TELEGRAM_TOKEN, main(), Запуск бота (polling, для локальної розробки)., Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli (+35 more)

### Community 3 - "Cron & Admin Utilities"
Cohesion: 0.07
Nodes (42): CRON_SECRET, HELP_PHONE, datetime, get_client_by_id(), get_cron_last_run(), Дата (ISO) останнього запуску щоденної задачі з цим ключем. None, якщо ще не зап, Позначити, що щоденна задача виконана сьогодні (ISO-дата)., Знайти клієнта за внутрішнім id. (+34 more)

### Community 4 - "Pet Registration Flow"
Cohesion: 0.14
Nodes (43): parse_weight(), float, int, Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, Викликати Telegram-запит (reply_text/reply_location/...) з повторами.      Прокс, with_retry(), add_pet_start(), _ask_location() (+35 more)

### Community 5 - "Error Handling & Handler Setup"
Cohesion: 0.08
Nodes (34): ADMIN_GROUP_CHAT_ID, ADMIN_TOPIC_ID, handle_error(), DEFAULT_TYPE, Глобальний обробник помилок PTB.  Без нього виняток, що вилетів з будь-якого han, Єдина точка реєстрації всіх handler-ів (webhook_bot.py і bot.py)., tracked_records.ends_at column, object (+26 more)

### Community 6 - "Reschedule & Cancel Flow"
Cohesion: 0.12
Nodes (36): Exception, format_date_label(), 2026-08-01' -> '01.08 Сб' (для кнопок вибору дати)., _ask_reschedule_date(), _ask_reschedule_time(), _cancel_confirm_keyboard(), _confirm_reschedule(), _do_cancel() (+28 more)

### Community 7 - "Deployment Guide"
Cohesion: 0.06
Nodes (35): 1. Завантажити зміни на GitHub (на Mac), 1. Напиши боту в Telegram, 2. Оновити код на PythonAnywhere, 2. Перевір webhook статус, 3. Зупинити старий polling бот (якщо працює), 3. Подивись логи Flask, 4. Налаштувати Web App на PythonAnywhere, 5. Налаштувати WSGI файл (+27 more)

### Community 8 - "Altegio API Client"
Cohesion: 0.12
Nodes (34): create_client_record(), Створити порожній запис клієнта (реєстрацію заповнюємо покроково)., cancel_record(), create_record(), find_available_staff_for_slot(), find_client_by_phone(), get_available_dates(), get_available_times() (+26 more)

### Community 9 - "Project Plan & Architecture"
Cohesion: 0.06
Nodes (30): 0. Поточний стан і ключове рішення, Altegio API — що використовуємо, code:block1 (grooming-telegram-bot/), code:block2 (clients        id, tg_user_id (unique), altegio_client_id, p), code:block3 (Фаза 0 ✅ (фундамент + Altegio API + вебхуки)), Scheduler: PythonAnywhere Scheduled Task → HTTP endpoint, UI бота: Inline-кнопки + ConversationHandler, Архітектурні рішення (+22 more)

### Community 10 - "Pet Card UI"
Cohesion: 0.20
Nodes (23): _card_keyboard(), _card_text(), _delete_confirm_keyboard(), edit_cancel(), edit_field_start(), edit_field_value(), _edit_keyboard(), _format_date() (+15 more)

### Community 11 - "Groq AI Chat"
Cohesion: 0.11
Nodes (20): SYSTEM_PROMPT, Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., chat_histories (in-memory per-user dict), clear_chat_history(), get_response(), int, str (+12 more)

### Community 12 - "Claude Code Hooks"
Cohesion: 0.10
Nodes (10): .claude/settings.json (hook registration), deny(), main(), output, _rtk_audit_log(), format-on-save.sh script, graphify-remind.sh script, protect-files.sh script (+2 more)

### Community 13 - "Vaccine Reminder Sync"
Cohesion: 0.15
Nodes (16): date, get_clients_with_altegio_link(), Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)., parse_date(), bool, date, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні., clients.vaccine_due_date column (+8 more)

### Community 14 - "Hook Permissions Config"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 15 - "Feature Ideas Backlog"
Cohesion: 0.25
Nodes (7): 📍 Кнопки з локаціями салонів, 🔔 Нагадування про запис, 📸 Обробка фото, 📊 Статистика популярних запитань, 💬 Швидкі відповіді (FAQ кнопки), 💡 Ідеї для покращення бота Mr.Snoopy Grooming, 📅 Інтеграція з Google Calendar

## Ambiguous Edges - Review These
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to

## Knowledge Gaps
- **110 isolated node(s):** `str`, `int`, `bool`, `str`, `allow` (+105 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `register_handlers()` connect `Bot Entry Points & Setup` to `Supabase Client CRUD`, `Booking Flow (Дата/Час/Категорія)`, `Error Handling & Handler Setup`, `Reschedule & Cancel Flow`, `Pet Card UI`, `Groq AI Chat`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `AltegioError` connect `Reschedule & Cancel Flow` to `Altegio API Client`, `Booking Flow (Дата/Час/Категорія)`, `Pet Registration Flow`, `Vaccine Reminder Sync`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `Фази реалізації` connect `Project Plan & Architecture` to `Cron & Admin Utilities`, `Vaccine Reminder Sync`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `AltegioError` (e.g. with `DEFAULT_TYPE` and `str`) actually correct?**
  _`AltegioError` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `InlineKeyboardButton` (e.g. with `AltegioError` and `show_bookings()`) actually correct?**
  _`InlineKeyboardButton` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `str`, `Отримати відповідь від Groq для повідомлення користувача.`, `Очистити історію чату для користувача.` to the rest of the system?**
  _225 weakly-connected nodes found - possible documentation gaps or missing edges._