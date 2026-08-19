"""Тижневий бекап Supabase: повний дамп таблиць одним JSON-файлом у Telegram.

На безкоштовному тарифі Supabase автоматичних бекапів немає, а картки
улюбленців і зв'язка Telegram↔Altegio не існують більше ніде — Altegio про
тварин не знає взагалі. Копія свідомо йде в Telegram, а не на диск
PythonAnywhere: диск живе на тій самій машині, що й бот, тож не переживе
проблем з акаунтом — тобто не покриває половину сценаріїв, для яких бекап і
затівається.
"""
import json
import logging
from datetime import date, datetime, timedelta

from config import BACKUP_CHAT_ID
from db.client import supabase
from services import notifications
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

PAGE_SIZE = 1000  # наше припущення про стелю однієї відповіді PostgREST

# Таблиця -> колонка унікального ключа (усі — первинні). Порядок обов'язковий:
# без нього сторінкове читання може продублювати або пропустити рядки. У
# cron_state немає id — первинний ключ там текстовий `key`.
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

BACKUP_HOUR = 7  # Київ; не збігається з 9 і 10, коли cron шле повідомлення клієнтам
BACKUP_KEY = "backup"  # позначка успіху: дата суботи тижня
BACKUP_ATTEMPT_KEY = "backup_attempt"  # позначка спроби: сьогоднішня дата
SATURDAY = 5  # datetime.weekday(): понеділок 0 … субота 5, неділя 6


def _fetch_table(table: str, order_column: str) -> list[dict]:
    """Усі рядки таблиці, сторінками не більше PAGE_SIZE.

    Кожна наступна сторінка читається «від останнього ключа» (`.gt()`), а не за
    зсувом: зсув залежить від кількості вже прочитаного, тож видалення рядка між
    двома запитами зсуває решту, і один рядок тихо не потрапляє в дамп.
    Видалення в рантаймі реальні — `db/client.py::delete_pet()` і
    `delete_pending_notifications_for_record()` (останнє йде з обробки вебхука
    Altegio, тобто може статись посеред дампа).

    Зупиняємось на порожній сторінці, а не на першій коротшій за PAGE_SIZE:
    PAGE_SIZE — лише наше припущення про стелю PostgREST, а якщо `db-max-rows`
    на боці Supabase менший, перша ж сторінка прийде коротшою, і умова «коротша
    за PAGE_SIZE» вирішила б, що таблиця закінчилась. Для бекапу це найгірший
    клас помилки: файл виглядає нормальним, а даних у ньому немає. Ціна такої
    умови — один зайвий (порожній) запит у кінці.
    """
    rows: list[dict] = []
    last_key = None
    while True:
        query = supabase.table(table).select("*").order(order_column).limit(PAGE_SIZE)
        if last_key is not None:
            query = query.gt(order_column, last_key)
        batch = query.execute().data or []
        if not batch:
            return rows
        rows.extend(batch)
        last_key = batch[-1][order_column]


def build_dump() -> dict:
    """Повний дамп усіх таблиць із БД."""
    tables = {name: _fetch_table(name, order) for name, order in BACKUP_TABLES.items()}
    return {
        "created_at": datetime.now(KYIV_TZ).isoformat(),
        "counts": {name: len(rows) for name, rows in tables.items()},
        "tables": tables,
    }


def saturday_of_week(day: date) -> date:
    """Субота тижня, до якого належить день (тиждень від понеділка)."""
    return day - timedelta(days=day.weekday()) + timedelta(days=SATURDAY)


def is_backup_due(now: datetime, last_run: str | None, last_attempt: str | None) -> bool:
    """Чи пора робити тижневий бекап. Уся каденція — тут, у диспетчері дат немає.

    Рішення читає дві позначки з cron_state, бо однієї не достатньо:

    - `last_run` (успіх) — дата суботи цього тижня, а не номер ISO-тижня, бо
      колонка last_run_date типу date. Неділя лишена як підхват: якщо зовнішній
      cron (cron-job.org) проспить усю суботу, бекап зробиться в неділю, а не
      пропаде на тиждень. Позначка в обидва дні та сама, тож при успіху двічі за
      тиждень не вистрелить.
    - `last_attempt` (спроба) — сьогоднішня дата. Без неї стійкий збій (лежить
      Supabase, відмовляє Telegram) ретраївся б на кожному тику зовнішнього cron
      (~кожні 10 хвилин з суботи 07:00 до кінця неділі — близько 246 повних
      дампів по вісім читань Supabase кожен і стільки ж повідомлень в
      адмін-топік). Гранулярність доби дає задумані рівно дві спроби на тиждень:
      субота і підхват у неділю.
    """
    if now.weekday() < SATURDAY or now.hour < BACKUP_HOUR:
        return False
    if last_attempt == now.date().isoformat():
        return False
    return last_run != saturday_of_week(now.date()).isoformat()


def send_weekly_backup() -> bool:
    """Зібрати дамп і надіслати файлом власнику. True — Telegram підтвердив доставку."""
    if not BACKUP_CHAT_ID:
        # Не лише в лог: змінну треба додати в оточення PythonAnywhere руками,
        # тож це найімовірніший збій у проді, а зовні «нема бекапу» не
        # відрізнити від «бекап працює». Адмін-група налаштована окремою
        # змінною, тож цей канал живий саме тоді, коли BACKUP_CHAT_ID немає.
        logger.warning("BACKUP_CHAT_ID не задано — тижневий бекап нікуди слати")
        notifications.notify_admins(
            "⚠️ Тижневий бекап Supabase не робиться: не задано BACKUP_CHAT_ID.\n"
            "Треба додати змінну в оточення PythonAnywhere."
        )
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

    # Нульові таблиці лишаються в підписі: `ratings: 0` — це або норма, або
    # тривога (закрились права, таблицю перейменувала міграція, помилковий
    # delete), а зникнення рядка не помітно ніяк. Підпис — єдиний артефакт, який
    # власник читає, не відкриваючи файл.
    counts = ", ".join(f"{name}: {n}" for name, n in dump["counts"].items())
    # Розмір — і підтвердження в лозі, що бекап відбувся, і сигнал росту: коли
    # наблизиться до ліміту Telegram (50 МБ), пора додавати gzip.
    logger.info(f"🗄 Дамп Supabase зібрано: {len(content)} байт")
    delivered = notifications.send_telegram_document(
        BACKUP_CHAT_ID,
        f"mrsnoopy-backup-{today}.json",
        content,
        caption=f"🗄 Бекап Supabase {today}\n{counts}",
    )
    if not delivered:
        # Бекап, який тихо не працює півроку, гірший за відсутній —
        # про відсутній хоча б відомо.
        notifications.notify_admins(f"⚠️ Тижневий бекап Supabase не надіслався ({today}) — деталі в логах.")
    return delivered
