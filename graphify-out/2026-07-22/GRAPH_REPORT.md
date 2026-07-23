# Graph Report - grooming-telegram-bot  (2026-07-22)

## Corpus Check
- 38 files · ~21,215 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 469 nodes · 968 edges · 37 communities (20 shown, 17 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2d17ee77`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_БД-клієнт CRUD-операції (dbclient.py)|БД-клієнт: CRUD-операції (db/client.py)]]
- [[_COMMUNITY_Флоу запису локаціякатегоріяпослуга|Флоу запису: локація/категорія/послуга]]
- [[_COMMUNITY_Анкета чернетка улюбленця + ретраї|Анкета: чернетка улюбленця + ретраї]]
- [[_COMMUNITY_Підтвердження запису та створення в Altegio|Підтвердження запису та створення в Altegio]]
- [[_COMMUNITY_Утиліти датичасу|Утиліти дати/часу]]
- [[_COMMUNITY_Картки улюбленців (списокредагування)|Картки улюбленців (список/редагування)]]
- [[_COMMUNITY_Bootstrap вебхук-сервера (webhook_bot.py)|Bootstrap вебхук-сервера (webhook_bot.py)]]
- [[_COMMUNITY_Локальний entrypoint (bot.py) + конфіг|Локальний entrypoint (bot.py) + конфіг]]
- [[_COMMUNITY_Секрети конфігу + фази плану розвитку|Секрети конфігу + фази плану розвитку]]
- [[_COMMUNITY_Сповіщення адмінів|Сповіщення адмінів]]
- [[_COMMUNITY_AI-чат фолбек (Groq)|AI-чат фолбек (Groq)]]
- [[_COMMUNITY_Синхронізація коментаря Altegio|Синхронізація коментаря Altegio]]
- [[_COMMUNITY_Підбір послуг за породою|Підбір послуг за породою]]
- [[_COMMUNITY_Скрипт реєстрації webhook|Скрипт реєстрації webhook]]
- [[_COMMUNITY_Майбутні фази та беклог ідей|Майбутні фази та беклог ідей]]
- [[_COMMUNITY_Groq API конфіг|Groq API конфіг]]
- [[_COMMUNITY_ALTEGIO_PARTNER_TOKEN|ALTEGIO_PARTNER_TOKEN]]
- [[_COMMUNITY_ALTEGIO_USER_TOKEN|ALTEGIO_USER_TOKEN]]
- [[_COMMUNITY_Мапа локацій Altegio|Мапа локацій Altegio]]
- [[_COMMUNITY_ADMIN_GROUP_CHAT_ID|ADMIN_GROUP_CHAT_ID]]
- [[_COMMUNITY_ADMIN_TOPIC_ID|ADMIN_TOPIC_ID]]
- [[_COMMUNITY_WELCOME_MESSAGE|WELCOME_MESSAGE]]
- [[_COMMUNITY_Таблиця visit_extras|Таблиця visit_extras]]
- [[_COMMUNITY_Таблиця ratings|Таблиця ratings]]
- [[_COMMUNITY_Таблиця chat_messages|Таблиця chat_messages]]
- [[_COMMUNITY_IDEAS.md (беклог ідей)|IDEAS.md (беклог ідей)]]
- [[_COMMUNITY_Ідея FAQ меню|Ідея: FAQ меню]]
- [[_COMMUNITY_Ідея статистика питань|Ідея: статистика питань]]
- [[_COMMUNITY_PLAN.md (дорожня карта)|PLAN.md (дорожня карта)]]
- [[_COMMUNITY_Клавіатура вибору локації|Клавіатура вибору локації]]
- [[_COMMUNITY_Головне меню (клавіатура)|Головне меню (клавіатура)]]
- [[_COMMUNITY_Форматування дати|Форматування дати]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]

## God Nodes (most connected - your core abstractions)
1. `with_retry()` - 49 edges
2. `handle_callback()` - 30 edges
3. `AltegioError` - 27 edges
4. `InlineKeyboardButton` - 22 edges
5. `handle_callback()` - 19 edges
6. `Update` - 19 edges
7. `int` - 19 edges
8. `DEFAULT_TYPE` - 18 edges
9. `register_handlers()` - 18 edges
10. `handle_callback()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Google Calendar booking integration idea` --semantically_similar_to--> `Фаза 2 — Онлайн-запис на грумінг`  [INFERRED] [semantically similar]
  IDEAS.md → PLAN.md
- `Salon location inline buttons with geolocation idea` --semantically_similar_to--> `Фаза 2 — Онлайн-запис на грумінг`  [INFERRED] [semantically similar]
  IDEAS.md → PLAN.md
- `bool` --uses--> `AltegioError`  [INFERRED]
  handlers/my_bookings.py → services/altegio.py
- `str` --uses--> `AltegioError`  [INFERRED]
  handlers/my_bookings.py → services/altegio.py
- `Фаза 0 — Фундамент + інтеграція з Altegio` --references--> `altegio_webhook_route() (/altegio/webhook/<secret>)`  [EXTRACTED]
  PLAN.md → webhook_bot.py

## Hyperedges (group relationships)
- **Telegram Webhook Deployment Flow** — wsgi_application, webhook_bot_app, webhook_bot_webhook, set_webhook_set_webhook, config_telegram_token [INFERRED 0.85]
- **Cron Notification Dispatch Flow** — webhook_bot_cron, config_cron_secret, db_schema_notifications, db_client_mark_notification, plan_phase_4 [INFERRED 0.80]
- **Altegio Webhook Ingestion Flow** — webhook_bot_altegio_webhook_route, config_altegio_webhook_secret, services_altegio_webhook_process_event, db_schema_tracked_records, plan_phase_2 [INFERRED 0.85]
- **Registration ConversationHandler state flow (phone -> location -> name -> pets)** — handlers_registration_conversation, handlers_registration_start, handlers_registration_got_phone, handlers_registration_got_location, handlers_registration_got_name, handlers_registration_got_pet_name, handlers_registration_got_pet_breed, handlers_registration_got_pet_birth, handlers_registration_got_pet_weight, handlers_registration_got_pet_allergies, handlers_registration_got_pet_behavior, handlers_registration_got_pet_photo, handlers_registration_got_add_more, handlers_registration_cancel [EXTRACTED 1.00]
- **Booking inline-keyboard callback dispatch flow (bk_* )** — handlers_booking_handle_callback, handlers_booking__ask_location, handlers_booking__ask_category, handlers_booking__ask_service, handlers_booking__ask_date, handlers_booking__ask_time, handlers_booking__show_confirm, handlers_booking__confirm_booking [EXTRACTED 1.00]
- **Telegram update dispatch chain wired in register_handlers (order-dependent)** — handlers_setup_register_handlers, handlers_registration_conversation, handlers_pets_edit_conversation, handlers_pets_show_pets, handlers_pets_handle_callback, handlers_booking_book_start, handlers_booking_price_start, handlers_booking_handle_callback, handlers_my_bookings_show_bookings, handlers_my_bookings_handle_callback, handlers_ai_chat_handle_message [EXTRACTED 1.00]

## Communities (37 total, 17 thin omitted)

### Community 0 - "БД-клієнт: CRUD-операції (db/client.py)"
Cohesion: 0.06
Nodes (55): create_client_record(), create_notification(), create_pet(), delete_pet(), get_client_by_id(), get_client_by_phone(), get_client_by_tg_id(), get_last_past_tracked_record() (+47 more)

### Community 1 - "Флоу запису: локація/категорія/послуга"
Cohesion: 0.11
Nodes (53): _ask_date, _ask_location (booking), _format_price, _location_name, _pet_keyboard, _select_service, _show_confirm, _show_date_page (+45 more)

### Community 2 - "Анкета: чернетка улюбленця + ретраї"
Cohesion: 0.13
Nodes (46): parse_weight(), float, int, Розібрати вагу в кг (кома або крапка). None, якщо не число або поза межами 0.1–1, Викликати Telegram-запит (reply_text/reply_location/...) з повторами.      Прокс, with_retry(), _ask_location, _ask_pet_photo (+38 more)

### Community 3 - "Підтвердження запису та створення в Altegio"
Cohesion: 0.12
Nodes (39): _ask_category, _ask_time, _category_keyboard, _confirm_booking, _show_location_card, _request, cancel_record(), create_client() (+31 more)

### Community 4 - "Утиліти дати/часу"
Cohesion: 0.14
Nodes (31): datetime, format_date_label(), parse_iso_datetime(), str, Спільні валідатори полів анкети та карток улюбленців., 2026-08-01' -> '01.08 Сб' (для кнопок вибору дати)., Захисний парсинг timestamptz-рядка з Supabase/Altegio (інколи із 'Z' замість off, 2026-08-01', '10:00' -> aware ISO-рядок у Europe/Kyiv, для запису в timestamptz- (+23 more)

### Community 5 - "Картки улюбленців (список/редагування)"
Cohesion: 0.12
Nodes (34): date, parse_date(), bool, Розібрати дату у форматі ДД.ММ.РРРР. None, якщо формат/значення некоректні., _card_keyboard, _card_text, _delete_confirm_keyboard, _edit_keyboard (+26 more)

### Community 6 - "Bootstrap вебхук-сервера (webhook_bot.py)"
Cohesion: 0.12
Nodes (20): altegio_webhook_route(), cron(), ensure_initialized(), ensure_initialized_with_retries(), index(), initialize_application(), _is_loop_alive(), ensure_initialized() з повторами - проксі PythonAnywhere інколи віддає 503. (+12 more)

### Community 7 - "Локальний entrypoint (bot.py) + конфіг"
Cohesion: 0.07
Nodes (25): Application, main() (polling entrypoint), supabase client instance, main(), Запуск бота (polling, для локальної розробки)., chat_histories (in-memory per-user dict), get_response(), edit_conversation (pets ConversationHandler) (+17 more)

### Community 8 - "Секрети конфігу + фази плану розвитку"
Cohesion: 0.15
Nodes (18): normalize_phone(), Привести телефон до формату +380XXXXXXXXX. None, якщо номер не схожий на українс, Фаза 0 — Фундамент + інтеграція з Altegio, Фаза 8 — AI-помічник 2.0, Фаза 9 — Зв'язок з адміністратором, cron-job.org external scheduler hitting /cron endpoint, _format_dt, _handle (+10 more)

### Community 9 - "Сповіщення адмінів"
Cohesion: 0.11
Nodes (22): notify_admins(), notify_admins_async(), bool, int, str, Створення та відправка сповіщень.  Відправка йде напряму через Telegram Bot API, Надіслати повідомлення напряму через Bot API. Повертає True при успіху., Надіслати повідомлення в адмін-топік групи. True, якщо дійшло. (+14 more)

### Community 10 - "AI-чат фолбек (Groq)"
Cohesion: 0.12
Nodes (18): clear_chat_history(), get_response(), Отримати відповідь від Groq для повідомлення користувача., Очистити історію чату для користувача., int, str, handle_message(), DEFAULT_TYPE (+10 more)

### Community 11 - "Синхронізація коментаря Altegio"
Cohesion: 0.15
Nodes (16): Exception, bool, bool, str, AltegioError, Помилка звернення до Altegio API., _merge_comment, _pet_line (+8 more)

### Community 12 - "Підбір послуг за породою"
Cohesion: 0.20
Nodes (11): _ask_service, _category_type_key, _generic_breed_services, _match_services_by_breed, _service_row, _show_generic_fallback, _show_level_suggestion, _show_service_page (+3 more)

### Community 13 - "Скрипт реєстрації webhook"
Cohesion: 0.29
Nodes (7): check_webhook(), get_webhook_info(), Встановити webhook URL для бота., Отримати інформацію про поточний webhook. Повертає поточний url (None при помилц, --check: лише перевірити стан (нічого не змінює).      Локальний `bot.py` (polli, set_webhook(), str

### Community 14 - "Майбутні фази та беклог ідей"
Cohesion: 0.33
Nodes (6): Appointment reminder notifications idea, Photo-based pet consultations idea, Фаза 4 — Автоматичні нагадування + оцінки, Фаза 5 — Історія грумінгу + рекомендації майстра, Фаза 6 — Бонусна програма, Фаза 7 — Персональні пропозиції та автоматизація

### Community 18 - "ALTEGIO_PARTNER_TOKEN"
Cohesion: 0.18
Nodes (10): hooks, PostToolUse, PreToolUse, SessionStart, permissions, allow, defaultMode, deny (+2 more)

### Community 19 - "ALTEGIO_USER_TOKEN"
Cohesion: 0.67
Nodes (3): deny(), main(), output

## Ambiguous Edges - Review These
- `python-3.11.0 runtime pin` → `WEBHOOK_SETUP.md (deployment guide)`  [AMBIGUOUS]
  runtime.txt · relation: conceptually_related_to

## Knowledge Gaps
- **71 isolated node(s):** `context-recovery.sh script`, `format-on-save.sh script`, `protect-files.sh script`, `output`, `rtk-suggest.sh script` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `python-3.11.0 runtime pin` and `WEBHOOK_SETUP.md (deployment guide)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `datetime` connect `Утиліти дати/часу` to `БД-клієнт: CRUD-операції (db/client.py)`, `Флоу запису: локація/категорія/послуга`, `Картки улюбленців (список/редагування)`, `Секрети конфігу + фази плану розвитку`, `Сповіщення адмінів`?**
  _High betweenness centrality (0.265) - this node is a cross-community bridge._
- **Why does `register_handlers()` connect `Локальний entrypoint (bot.py) + конфіг` to `Флоу запису: локація/категорія/послуга`, `Утиліти дати/часу`, `Картки улюбленців (список/редагування)`, `Bootstrap вебхук-сервера (webhook_bot.py)`, `AI-чат фолбек (Groq)`?**
  _High betweenness centrality (0.224) - this node is a cross-community bridge._
- **Why does `handle_callback()` connect `Флоу запису: локація/категорія/послуга` to `Анкета: чернетка улюбленця + ретраї`, `Підтвердження запису та створення в Altegio`, `Утиліти дати/часу`, `Картки улюбленців (список/редагування)`, `Локальний entrypoint (bot.py) + конфіг`, `Підбір послуг за породою`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `AltegioError` (e.g. with `DEFAULT_TYPE` and `str`) actually correct?**
  _`AltegioError` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `InlineKeyboardButton` (e.g. with `AltegioError` and `show_bookings()`) actually correct?**
  _`InlineKeyboardButton` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `context-recovery.sh script`, `format-on-save.sh script`, `protect-files.sh script` to the rest of the system?**
  _170 weakly-connected nodes found - possible documentation gaps or missing edges._