"""Тижневий бекап Supabase: повний дамп таблиць одним JSON-файлом у Telegram.

На безкоштовному тарифі Supabase автоматичних бекапів немає, а картки
улюбленців і зв'язка Telegram↔Altegio не існують більше ніде — Altegio про
тварин не знає взагалі. Копія свідомо йде в Telegram, а не на диск
PythonAnywhere: диск живе на тій самій машині, що й бот, тож не переживе
проблем з акаунтом — тобто не покриває половину сценаріїв, для яких бекап і
затівається.
"""
from datetime import datetime

from db.client import supabase
from services.notifications import KYIV_TZ

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
