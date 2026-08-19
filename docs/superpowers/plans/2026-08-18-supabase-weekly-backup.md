# Тижневий бекап Supabase у Telegram — план реалізації

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Раз на тиждень бот сам надсилає повний дамп бази Supabase одним JSON-файлом в особистий чат власника в Telegram.

**Architecture:** Новий `services/backup.py` збирає дамп усіх таблиць через Supabase REST (сторінками по 1000 рядків) і віддає його `notifications.send_telegram_document()` — новій функції на тій самій `requests.Session` з ретраями, що й решта cron-відправок. Запуск — нова гілка в `services/scheduler.py::_run_daily_tasks()`, гейтована через `cron_state` датою суботи поточного тижня.

**Tech Stack:** Python 3.13, `supabase-py` (REST), `requests`, `unittest` + `unittest.mock`, зовнішній cron (cron-job.org) → `/cron/<CRON_SECRET>`.

## Global Constraints

- Спека: `docs/superpowers/specs/2026-08-18-supabase-backup-design.md` — при розходженні правий документ спеки.
- Мова коментарів і повідомлень — українська, як у решті коду.
- Жодних нових залежностей: `requests` і `supabase-py` вже в `requirements.txt`.
- Тести — `unittest` + `unittest.mock`, без мережі й без звернень до справжніх Supabase/Telegram.
- Запуск тестів: `venv/bin/python -m unittest services.test_<модуль> -v` (автоматичний `discover` у цьому проєкті не працює).
- Дамп містить телефони й імена клієнтів: адресат — лише `BACKUP_CHAT_ID` (приватний чат), ніколи не адмін-група.
- Позначка в `cron_state` ставиться лише після підтвердженої доставки.
- `BACKUP_CHAT_ID` = `651807767` (приватний чат `@Nifargo`, підтверджено через `getChat`). Значення живе лише в `.env` і у змінних оточення PythonAnywhere — у `config.py` жодних дефолтів, щоб адресат не «зашився» в код.

---

## File Structure

| Файл | Відповідальність |
|------|------------------|
| `services/backup.py` (створити) | Збірка дампа, рішення «чи пора», відправка файла. Уся доменна логіка бекапу. |
| `services/notifications.py` (змінити) | Додати `send_telegram_document()` — транспорт файла до Bot API. |
| `config.py` (змінити) | `BACKUP_CHAT_ID` з оточення. |
| `services/scheduler.py` (змінити) | Одна гілка в `_run_daily_tasks()`: виклик і позначка в `cron_state`. |
| `services/test_notifications_document.py` (створити) | Тест транспорту файла. |
| `services/test_backup.py` (створити) | Тести дампа, пагінації, гейтування, обробки збоїв. |
| `CLAUDE.md`, `PLAN.md` (змінити) | Опис механізму, чекліст «нова таблиця → у `BACKUP_TABLES`», закриття ризику №10. |

Чому `BACKUP_HOUR`/`BACKUP_KEY` живуть у `services/backup.py`, а не в `scheduler.py`, де лежать години решти щоденних задач: рішення «чи пора» винесене в чисту функцію `is_backup_due(now, last_run)`, щоб гейтування тестувалось без моків планувальника — а їй потрібна година. У `scheduler.py` лишається лише виклик.

---

## Task 1: Транспорт файла до Telegram

**Files:**
- Modify: `services/notifications.py` (додати функцію після `send_telegram_message`, тобто після рядка 59)
- Test: `services/test_notifications_document.py` (створити)

**Interfaces:**
- Consumes: наявні модульні `_session`, `_API_URL`, `logger` у `services/notifications.py`.
- Produces: `send_telegram_document(chat_id: int, filename: str, content: bytes, caption: str | None = None) -> bool` — `True`, якщо Telegram прийняв файл.

- [ ] **Step 1: Написати тест, що падає**

Створити `services/test_notifications_document.py`:

```python
"""send_telegram_document(): файл іде в sendDocument як multipart, помилка HTTP → False."""
import unittest
from unittest.mock import MagicMock, patch

from services import notifications


class SendDocumentTest(unittest.TestCase):
    @patch("services.notifications._session")
    def test_sends_file_as_multipart(self, session):
        session.post.return_value = MagicMock(ok=True)

        result = notifications.send_telegram_document(
            42, "backup.json", b'{"a": 1}', caption="бекап",
        )

        self.assertTrue(result)
        self.assertTrue(session.post.call_args.args[0].endswith("/sendDocument"))
        kwargs = session.post.call_args.kwargs
        self.assertEqual(kwargs["data"], {"chat_id": 42, "caption": "бекап"})
        self.assertEqual(kwargs["files"]["document"][0], "backup.json")
        self.assertEqual(kwargs["files"]["document"][1], b'{"a": 1}')

    @patch("services.notifications._session")
    def test_http_error_returns_false(self, session):
        session.post.return_value = MagicMock(ok=False, status_code=400, text="Bad Request")

        result = notifications.send_telegram_document(42, "backup.json", b"{}")

        self.assertFalse(result)

    @patch("services.notifications._session")
    def test_caption_omitted_when_not_given(self, session):
        session.post.return_value = MagicMock(ok=True)

        notifications.send_telegram_document(42, "backup.json", b"{}")

        self.assertEqual(session.post.call_args.kwargs["data"], {"chat_id": 42})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустити тест і переконатись, що падає**

Run: `venv/bin/python -m unittest services.test_notifications_document -v`
Expected: FAIL — `AttributeError: module 'services.notifications' has no attribute 'send_telegram_document'`

- [ ] **Step 3: Реалізувати мінімум**

У `services/notifications.py` після `send_telegram_message()` (рядок 59) додати:

```python
def send_telegram_document(
    chat_id: int, filename: str, content: bytes, caption: str | None = None,
) -> bool:
    """Надіслати файл напряму через Bot API. Повертає True при успіху.

    `content` — саме bytes, а не відкритий файл: Session-level ретраї на
    502/503/504 (проксі PythonAnywhere) повторюють запит, а вичерпаний
    файловий об'єкт при повторі віддав би порожнє тіло.
    """
    data: dict = {"chat_id": chat_id}
    if caption is not None:
        data["caption"] = caption
    try:
        response = _session.post(
            f"{_API_URL}/sendDocument",
            data=data,
            files={"document": (filename, content, "application/json")},
            timeout=60,  # більше за 15s у sendMessage: тут вантажиться файл
        )
        if not response.ok:
            logger.error(f"Telegram sendDocument {chat_id}: HTTP {response.status_code} {response.text[:200]}")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"Telegram sendDocument {chat_id}: {e}")
        return False
```

- [ ] **Step 4: Запустити тест і переконатись, що проходить**

Run: `venv/bin/python -m unittest services.test_notifications_document -v`
Expected: PASS (3 тести)

- [ ] **Step 5: Переконатись, що наявні тести відправки не зламані**

Run: `venv/bin/python -m unittest services.test_notifications_retry -v`
Expected: PASS

- [ ] **Step 6: Коміт**

```bash
git add services/notifications.py services/test_notifications_document.py
git commit -m "Додати відправку файла через Telegram sendDocument"
```

---

## Task 2: Збірка дампа з Supabase

**Files:**
- Create: `services/backup.py`
- Test: `services/test_backup.py` (створити)

**Interfaces:**
- Consumes: `supabase` з `db.client`, `KYIV_TZ` з `services.notifications`.
- Produces:
  - `BACKUP_TABLES: dict[str, str]` — таблиця → колонка сортування.
  - `PAGE_SIZE: int = 1000`
  - `build_dump() -> dict` — `{"created_at": str, "counts": dict[str, int], "tables": dict[str, list[dict]]}`

- [ ] **Step 1: Написати тест, що падає**

Створити `services/test_backup.py`:

```python
"""build_dump(): усі таблиці в дампі, великі таблиці читаються сторінками."""
import unittest
from unittest.mock import MagicMock, patch

from services import backup


class BuildDumpTest(unittest.TestCase):
    def _range_call(self, supabase):
        """Ланка .range() у ланцюжку supabase.table().select().order().range()."""
        return supabase.table.return_value.select.return_value.order.return_value.range

    @patch("services.backup.supabase")
    def test_dump_contains_every_table_and_counts(self, supabase):
        self._range_call(supabase).return_value.execute.return_value = MagicMock(data=[])

        dump = backup.build_dump()

        self.assertEqual(set(dump["tables"]), set(backup.BACKUP_TABLES))
        self.assertEqual(set(dump["counts"]), set(backup.BACKUP_TABLES))
        self.assertIn("created_at", dump)

    @patch("services.backup.BACKUP_TABLES", {"clients": "id"})
    @patch("services.backup.PAGE_SIZE", 2)
    @patch("services.backup.supabase")
    def test_reads_all_pages_when_table_exceeds_page_size(self, supabase):
        range_call = self._range_call(supabase)
        range_call.return_value.execute.side_effect = [
            MagicMock(data=[{"id": 1}, {"id": 2}]),
            MagicMock(data=[{"id": 3}]),
        ]

        dump = backup.build_dump()

        self.assertEqual(dump["counts"], {"clients": 3})
        self.assertEqual(len(dump["tables"]["clients"]), 3)
        self.assertEqual([c.args for c in range_call.call_args_list], [(0, 1), (2, 3)])

    @patch("services.backup.BACKUP_TABLES", {"cron_state": "key"})
    @patch("services.backup.supabase")
    def test_sorts_by_declared_column(self, supabase):
        self._range_call(supabase).return_value.execute.return_value = MagicMock(data=[])

        backup.build_dump()

        order_call = supabase.table.return_value.select.return_value.order
        self.assertEqual(order_call.call_args.args, ("key",))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустити тест і переконатись, що падає**

Run: `venv/bin/python -m unittest services.test_backup -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'services.backup'`

- [ ] **Step 3: Реалізувати мінімум**

Створити `services/backup.py`:

```python
"""Тижневий бекап Supabase: повний дамп таблиць одним JSON-файлом у Telegram.

На безкоштовному тарифі Supabase автоматичних бекапів немає, а картки
улюбленців і зв'язка Telegram↔Altegio не існують більше ніде — Altegio про
тварин не знає взагалі. Копія свідомо йде в Telegram, а не на диск
PythonAnywhere: диск живе на тій самій машині, що й бот, тож не переживе
проблем з акаунтом — тобто не покриває половину сценаріїв, для яких бекап і
затівається.
"""
import logging
from datetime import datetime

from db.client import supabase
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

PAGE_SIZE = 1000  # Supabase REST більше за один запит не віддає

# Таблиця -> колонка сортування. Порядок обов'язковий: без нього .range()
# може продублювати або пропустити рядки між сторінками. У cron_state немає
# id — первинний ключ там текстовий `key`.
#
# Список явний, а не автовизначений: Supabase REST не вміє перелічувати
# таблиці. Побічний ефект корисний — нову таблицю доводиться свідомо додати
# сюди (див. чекліст у CLAUDE.md), інакше вона не потрапить у бекап.
BACKUP_TABLES = {
    "clients": "id",
    "pets": "id",
    "tracked_records": "id",
    "visit_extras": "id",
    "ratings": "id",
    "notifications": "id",
    "chat_messages": "id",
    "cron_state": "key",
}


def _fetch_table(table: str, order_column: str) -> list[dict]:
    """Усі рядки таблиці, сторінками по PAGE_SIZE."""
    rows: list[dict] = []
    while True:
        page = (
            supabase.table(table)
            .select("*")
            .order(order_column)
            .range(len(rows), len(rows) + PAGE_SIZE - 1)
            .execute()
        )
        batch = page.data or []
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            return rows


def build_dump() -> dict:
    """Повний дамп усіх таблиць із БД."""
    tables = {name: _fetch_table(name, order) for name, order in BACKUP_TABLES.items()}
    return {
        "created_at": datetime.now(KYIV_TZ).isoformat(),
        "counts": {name: len(rows) for name, rows in tables.items()},
        "tables": tables,
    }
```

- [ ] **Step 4: Запустити тест і переконатись, що проходить**

Run: `venv/bin/python -m unittest services.test_backup -v`
Expected: PASS (3 тести)

- [ ] **Step 5: Коміт**

```bash
git add services/backup.py services/test_backup.py
git commit -m "Додати збірку повного дампа Supabase зі сторінковим читанням"
```

---

## Task 3: Тижневе гейтування і відправка дампа

**Files:**
- Modify: `config.py` (після рядка 40, поряд з `ADMIN_TOPIC_ID`)
- Modify: `services/backup.py` (додати константи й функції)
- Modify: `services/test_backup.py` (додати класи тестів)
- Modify: `.env` (локально; у git не потрапляє)

**Interfaces:**
- Consumes: `build_dump()` з Task 2, `notifications.send_telegram_document()` з Task 1, `notifications.notify_admins()` (наявна).
- Produces:
  - `BACKUP_HOUR: int = 7`, `BACKUP_KEY: str = "backup"`, `SATURDAY: int = 5`
  - `saturday_of_week(day: date) -> date`
  - `is_backup_due(now: datetime, last_run: str | None) -> bool`
  - `send_weekly_backup() -> bool`

- [ ] **Step 1: Написати тести, що падають**

Дописати в `services/test_backup.py` (після `BuildDumpTest`):

```python
class BackupDueTest(unittest.TestCase):
    """Субота — штатний день; неділя — підхват, якщо cron проспав суботу."""

    def test_due_on_saturday_after_hour(self):
        now = datetime(2026, 8, 22, 7, 5, tzinfo=backup.KYIV_TZ)  # субота
        self.assertTrue(backup.is_backup_due(now, None))

    def test_not_due_before_hour(self):
        now = datetime(2026, 8, 22, 6, 59, tzinfo=backup.KYIV_TZ)
        self.assertFalse(backup.is_backup_due(now, None))

    def test_not_due_on_weekday(self):
        now = datetime(2026, 8, 19, 12, 0, tzinfo=backup.KYIV_TZ)  # середа
        self.assertFalse(backup.is_backup_due(now, None))

    def test_not_due_twice_in_same_week(self):
        now = datetime(2026, 8, 22, 9, 0, tzinfo=backup.KYIV_TZ)
        self.assertFalse(backup.is_backup_due(now, "2026-08-22"))

    def test_sunday_catches_up_missed_saturday(self):
        now = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)  # неділя
        self.assertTrue(backup.is_backup_due(now, None))

    def test_sunday_skipped_when_saturday_done(self):
        now = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)
        self.assertFalse(backup.is_backup_due(now, "2026-08-22"))

    def test_due_again_next_week(self):
        now = datetime(2026, 8, 29, 7, 0, tzinfo=backup.KYIV_TZ)  # наступна субота
        self.assertTrue(backup.is_backup_due(now, "2026-08-22"))

    def test_saturday_of_week_is_same_for_saturday_and_sunday(self):
        saturday = date(2026, 8, 22)
        sunday = date(2026, 8, 23)
        self.assertEqual(backup.saturday_of_week(saturday), saturday)
        self.assertEqual(backup.saturday_of_week(sunday), saturday)


class SendWeeklyBackupTest(unittest.TestCase):
    @patch("services.backup.BACKUP_CHAT_ID", None)
    @patch("services.backup.notifications")
    @patch("services.backup.build_dump")
    def test_does_nothing_without_chat_id(self, build_dump, notifications):
        result = backup.send_weekly_backup()

        self.assertFalse(result)
        notifications.send_telegram_document.assert_not_called()
        build_dump.assert_not_called()

    @patch("services.backup.BACKUP_CHAT_ID", 42)
    @patch("services.backup.notifications")
    @patch("services.backup.build_dump")
    def test_sends_json_file_with_counts_in_caption(self, build_dump, notifications):
        build_dump.return_value = {
            "created_at": "2026-08-22T07:00:00+03:00",
            "counts": {"clients": 3, "pets": 4, "ratings": 0},
            "tables": {"clients": [{"id": 1}], "pets": [], "ratings": []},
        }
        notifications.send_telegram_document.return_value = True

        result = backup.send_weekly_backup()

        self.assertTrue(result)
        args = notifications.send_telegram_document.call_args
        self.assertEqual(args.args[0], 42)
        self.assertTrue(args.args[1].startswith("mrsnoopy-backup-"))
        self.assertTrue(args.args[1].endswith(".json"))
        self.assertIn(b'"clients"', args.args[2])
        self.assertIn("clients: 3", args.kwargs["caption"])
        notifications.notify_admins.assert_not_called()

    @patch("services.backup.BACKUP_CHAT_ID", 42)
    @patch("services.backup.notifications")
    @patch("services.backup.build_dump")
    def test_failed_delivery_notifies_admins(self, build_dump, notifications):
        build_dump.return_value = {"created_at": "x", "counts": {"clients": 3}, "tables": {"clients": []}}
        notifications.send_telegram_document.return_value = False

        result = backup.send_weekly_backup()

        self.assertFalse(result)
        notifications.notify_admins.assert_called_once()

    @patch("services.backup.BACKUP_CHAT_ID", 42)
    @patch("services.backup.notifications")
    @patch("services.backup.build_dump")
    def test_dump_failure_notifies_admins_and_does_not_send(self, build_dump, notifications):
        build_dump.side_effect = RuntimeError("Supabase недоступний")

        result = backup.send_weekly_backup()

        self.assertFalse(result)
        notifications.send_telegram_document.assert_not_called()
        notifications.notify_admins.assert_called_once()
```

Дописати імпорти у верх `services/test_backup.py`:

```python
from datetime import date, datetime
```

- [ ] **Step 2: Запустити тести і переконатись, що падають**

Run: `venv/bin/python -m unittest services.test_backup -v`
Expected: FAIL — `AttributeError: module 'services.backup' has no attribute 'is_backup_due'`

- [ ] **Step 3: Додати змінну оточення**

У `config.py` після рядка 40 (`ADMIN_TOPIC_ID`) додати:

```python
# Куди слати тижневий бекап Supabase. Особистий чат власника, свідомо окремо
# від ADMIN_GROUP_CHAT_ID: дамп містить імена й телефони клієнтів і не має
# шансу опинитись у спільній групі з персоналом.
BACKUP_CHAT_ID = int(os.getenv("BACKUP_CHAT_ID")) if os.getenv("BACKUP_CHAT_ID") else None
```

У локальний `.env` додати рядок (у git файл не потрапляє):

```
BACKUP_CHAT_ID=651807767
```

- [ ] **Step 4: Реалізувати гейтування і відправку**

У `services/backup.py` привести імпорти до вигляду:

```python
import json
import logging
from datetime import date, datetime, timedelta

from config import BACKUP_CHAT_ID
from db.client import supabase
from services import notifications
from services.notifications import KYIV_TZ
```

Після `BACKUP_TABLES` додати константи:

```python
BACKUP_HOUR = 7  # Київ; не збігається з 9 і 10, коли cron шле повідомлення клієнтам
BACKUP_KEY = "backup"
SATURDAY = 5  # datetime.weekday(): понеділок 0 … субота 5, неділя 6
```

Після `build_dump()` додати:

```python
def saturday_of_week(day: date) -> date:
    """Субота тижня, до якого належить день (тиждень від понеділка)."""
    return day - timedelta(days=day.weekday()) + timedelta(days=SATURDAY)


def is_backup_due(now: datetime, last_run: str | None) -> bool:
    """Чи пора робити тижневий бекап.

    Позначка в cron_state — дата суботи цього тижня, а не номер ISO-тижня, бо
    колонка last_run_date типу date. Неділя лишена як підхват: якщо зовнішній
    cron (cron-job.org) проспить усю суботу, бекап зробиться в неділю, а не
    пропаде на тиждень. Позначка в обидва дні та сама, тож двічі не вистрелить.
    """
    if now.weekday() < SATURDAY or now.hour < BACKUP_HOUR:
        return False
    return last_run != saturday_of_week(now.date()).isoformat()


def send_weekly_backup() -> bool:
    """Зібрати дамп і надіслати файлом власнику. True — Telegram підтвердив доставку."""
    if not BACKUP_CHAT_ID:
        logger.warning("BACKUP_CHAT_ID не задано — тижневий бекап нікуди слати")
        return False

    today = datetime.now(KYIV_TZ).date().isoformat()
    try:
        dump = build_dump()
        # default=str страхує від numeric, який PostgREST може віддати як Decimal
        # (pets.weight); ensure_ascii=False — щоб імена лишились читабельними.
        content = json.dumps(dump, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    except Exception as e:
        logger.error(f"❌ Не вдалося зібрати дамп Supabase: {e}", exc_info=True)
        notifications.notify_admins(f"⚠️ Тижневий бекап Supabase не зібрався ({today}): {e}")
        return False

    counts = ", ".join(f"{name}: {n}" for name, n in dump["counts"].items() if n)
    delivered = notifications.send_telegram_document(
        BACKUP_CHAT_ID,
        f"mrsnoopy-backup-{today}.json",
        content,
        caption=f"🗄 Бекап Supabase {today}\n{counts or 'усі таблиці порожні'}",
    )
    if not delivered:
        # Бекап, який тихо не працює півроку, гірший за відсутній —
        # про відсутній хоча б відомо.
        notifications.notify_admins(f"⚠️ Тижневий бекап Supabase не надіслався ({today}) — деталі в логах.")
    return delivered
```

- [ ] **Step 5: Запустити тести і переконатись, що проходять**

Run: `venv/bin/python -m unittest services.test_backup -v`
Expected: PASS (15 тестів: 3 з Task 2, 8 гейтування, 4 відправки)

- [ ] **Step 6: Коміт**

```bash
git add config.py services/backup.py services/test_backup.py
git commit -m "Додати тижневе гейтування і відправку бекапу власнику"
```

---

## Task 4: Підключення до cron-диспетчера

**Files:**
- Modify: `services/scheduler.py` (рядок 14 — імпорт; після рядка 213 — нова гілка)
- Test: `services/test_backup.py` (додати клас `SchedulerWiringTest`)

**Interfaces:**
- Consumes: `backup.is_backup_due()`, `backup.send_weekly_backup()`, `backup.saturday_of_week()`, `backup.BACKUP_KEY` з Task 3; наявні `db.get_cron_last_run()` / `db.set_cron_last_run()`.
- Produces: нічого для наступних задач.

- [ ] **Step 1: Написати тест, що падає**

Дописати в `services/test_backup.py`:

```python
class SchedulerWiringTest(unittest.TestCase):
    """Гілка в _run_daily_tasks(): бекап викликається і позначається датою суботи."""

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_saturday_run_marks_week_done(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 22, 7, 30, tzinfo=backup.KYIV_TZ)
        db.get_cron_last_run.return_value = None
        mock_backup.is_backup_due.return_value = True
        mock_backup.send_weekly_backup.return_value = True
        mock_backup.saturday_of_week.return_value = date(2026, 8, 22)
        mock_backup.BACKUP_KEY = "backup"

        scheduler._run_daily_tasks()

        mock_backup.send_weekly_backup.assert_called_once()
        db.set_cron_last_run.assert_any_call("backup", "2026-08-22")

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_failed_backup_does_not_mark_week_done(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 22, 7, 30, tzinfo=backup.KYIV_TZ)
        db.get_cron_last_run.return_value = None
        mock_backup.is_backup_due.return_value = True
        mock_backup.send_weekly_backup.return_value = False
        mock_backup.saturday_of_week.return_value = date(2026, 8, 22)
        mock_backup.BACKUP_KEY = "backup"

        scheduler._run_daily_tasks()

        calls = [c.args for c in db.set_cron_last_run.call_args_list]
        self.assertNotIn(("backup", "2026-08-22"), calls)
```

- [ ] **Step 2: Запустити тести і переконатись, що падають**

Run: `venv/bin/python -m unittest services.test_backup.SchedulerWiringTest -v`
Expected: FAIL — `AttributeError: <module 'services.scheduler'> does not have the attribute 'backup'`

- [ ] **Step 3: Підключити до диспетчера**

У `services/scheduler.py` рядок 14 замінити на:

```python
from services import altegio_reconcile, backup, birthday, notifications, rebook_promo, vaccine_sync
```

У `_run_daily_tasks()` після гілки `REBOOK_PROMO_KEY` (після рядка 213) додати:

```python
    # Єдина задача не з добовою, а з тижневою каденцією, тому власне рішення
    # «чи пора» (субота/неділя + година) живе в backup.is_backup_due(), а в
    # cron_state пишеться дата суботи цього тижня, а не `today`.
    if backup.is_backup_due(now, db.get_cron_last_run(backup.BACKUP_KEY)):
        try:
            success = backup.send_weekly_backup()
        except Exception as e:
            logger.error(f"❌ Помилка тижневого бекапу Supabase: {e}", exc_info=True)
            success = False
        if success:
            db.set_cron_last_run(backup.BACKUP_KEY, backup.saturday_of_week(now.date()).isoformat())
```

- [ ] **Step 4: Запустити тести і переконатись, що проходять**

Run: `venv/bin/python -m unittest services.test_backup -v`
Expected: PASS (17 тестів)

- [ ] **Step 5: Переконатись, що решта тестів жива**

Run: `venv/bin/python -m unittest services.test_altegio_webhook services.test_visit_history services.test_rebook_promo services.test_birthday services.test_altegio_reconcile services.test_notifications_document handlers.test_rebook_promo -v`
Expected: PASS

- [ ] **Step 6: Коміт**

```bash
git add services/scheduler.py services/test_backup.py
git commit -m "Підключити тижневий бекап до cron-диспетчера"
```

---

## Task 5: Документація і жива перевірка

**Files:**
- Modify: `CLAUDE.md` (таблиця Key files; блок Architecture — cron; список Env variables; розділ Deployment)
- Modify: `PLAN.md` (ризик №10)

**Interfaces:**
- Consumes: усе з Task 1–4.
- Produces: нічого для коду.

- [ ] **Step 1: Оновити `CLAUDE.md`**

У таблицю **Key files** додати рядок після `services/scheduler.py`:

```markdown
| `services/backup.py` | Тижневий дамп усіх таблиць Supabase → JSON-файл в особистий чат власника (субота, `cron_state` ключ `backup`) |
```

У блок `Architecture` (схема cron) після рядка про обробник по типу додати:

```
 → щотижня (сб/нд після 7:00 Київ) backup.send_weekly_backup() → JSON-дамп у BACKUP_CHAT_ID
```

У список **Env variables** додати:

```
BACKUP_CHAT_ID=... # особистий чат власника для тижневого бекапу (НЕ адмін-група: дамп містить телефони клієнтів)
```

У розділ **Deployment** додати пункт:

```markdown
- Після додавання нової таблиці в схему: внести її в `BACKUP_TABLES` (`services/backup.py`), інакше вона не потрапить у тижневий бекап
```

- [ ] **Step 2: Оновити `PLAN.md`**

Ризик №10 — це рядок таблиці ризиків, `PLAN.md:525`. Поточний текст:

```markdown
| 10 | Бекапи | На free tier Supabase немає автоматичних бекапів. Раз на день scheduled task робить експорт ключових таблиць (CSV/JSON) на диск PythonAnywhere. Додати у Фазу 0. |
```

Замінити на:

```markdown
| 10 | Бекапи | ✅ Закрито 2026-08-18: `services/backup.py` щотижня (субота, підхват у неділю) надсилає повний JSON-дамп усіх таблиць в особистий чат власника в Telegram. Від початкового «експорту на диск PythonAnywhere» свідомо відмовились: копія на тій самій машині, що й бот, не переживає проблем з акаунтом, тобто не покриває половину сценаріїв, для яких бекап і потрібен. Скрипт відновлення навмисно не писався — перевірити його можна лише на живій базі або на окремому тестовому проєкті Supabase, а неперевірений скрипт дає хибне відчуття безпеки. Спека: `docs/superpowers/specs/2026-08-18-supabase-backup-design.md`. |
```

- [ ] **Step 3: Коміт документації**

```bash
git add CLAUDE.md PLAN.md
git commit -m "Задокументувати тижневий бекап і закрити ризик №10"
```

- [ ] **Step 4: Жива перевірка на PythonAnywhere**

Не чекаючи суботи (`send_weekly_backup()` не читає й не пише `cron_state`, тож ручний виклик нічого не зіпсує):

1. Задеплоїти гілку і додати `BACKUP_CHAT_ID=651807767` у змінні оточення веб-аппа, перезавантажити його.
2. У Bash-консолі PythonAnywhere:

```bash
cd ~/MRS_elegram_bot && python3 -c "from services import backup; print(backup.send_weekly_backup())"
```

Expected: `True`, а в особистому чаті з ботом — файл `mrsnoopy-backup-<дата>.json` із підписом і непорожніми `counts`.

3. Відкрити файл і переконатись, що в `tables.clients` є рядки, а `tables.pets` містить картки улюбленців.

- [ ] **Step 5: Перевірити сценарій збою**

У тій самій консолі (з навмисно хибним адресатом):

```bash
cd ~/MRS_elegram_bot && python3 -c "
from services import backup
backup.BACKUP_CHAT_ID = 1
print(backup.send_weekly_backup())
"
```

Expected: `False`, і в адмін-топіку — попередження «Тижневий бекап Supabase не надіслався».

- [ ] **Step 6: Створити PR** (граф перебудовує post-commit хук graphify — окремих дій не потрібно)

```bash
git push -u origin feature/supabase-weekly-backup
gh pr create --title "Тижневий бекап Supabase у Telegram" --body "Закриває ризик №10. Спека: docs/superpowers/specs/2026-08-18-supabase-backup-design.md"
```

---

## Self-Review

**Покриття спеки:**

| Вимога спеки | Задача |
|--------------|--------|
| Вісім таблиць, `select("*")` | Task 2 (`BACKUP_TABLES`) |
| Пагінація по 1000 через `.range()` | Task 2 (`_fetch_table`, тест сторінок) |
| Один JSON-файл `mrsnoopy-backup-YYYY-MM-DD.json` зі `created_at`/`counts`/`tables` | Task 2 + Task 3 |
| Без gzip, без CSV | Task 3 (`json.dumps` → bytes) |
| Субота, година ≥ 7, підхват у неділю, раз на тиждень | Task 3 (`is_backup_due`) + Task 4 (гілка) |
| Позначка = дата суботи, бо колонка `date` | Task 3 + Task 4 |
| `BACKUP_CHAT_ID` окремо від адмін-групи, незадана → мовчить | Task 3 |
| `send_telegram_document()` на `_session` з ретраями | Task 1 |
| Позначка лише після підтвердженої доставки | Task 4 (тест невдачі) |
| Помилка → лог + сповіщення адмінам | Task 3 (два тести) |
| Тести: збірка, пагінація, гейтування, провал відправки | Task 2, Task 3 |
| Чекліст «нова таблиця → `BACKUP_TABLES`» | Task 5 |

Прогалин немає.

**Заглушки:** перевірено — кожен крок містить готовий код або точну команду з очікуваним результатом.

**Узгодженість імен:** `BACKUP_TABLES`, `PAGE_SIZE`, `_fetch_table`, `build_dump`, `BACKUP_HOUR`, `BACKUP_KEY`, `SATURDAY`, `saturday_of_week`, `is_backup_due`, `send_weekly_backup`, `send_telegram_document` — однакові в усіх задачах і тестах. Дата 2026-08-22 у тестах — субота, 2026-08-23 — неділя, 2026-08-19 — середа, 2026-08-29 — наступна субота.
