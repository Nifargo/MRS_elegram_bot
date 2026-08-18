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
    """Усі рядки таблиці, сторінками не більше PAGE_SIZE.

    Зупиняємось на порожній сторінці, а не на першій коротшій за PAGE_SIZE, і
    зсув рахуємо від фактично отриманої кількості рядків. PAGE_SIZE — лише наше
    припущення про стелю PostgREST: якщо `db-max-rows` на боці Supabase
    менший, перша ж сторінка прийде коротшою, і умова «коротша за PAGE_SIZE»
    вирішила б, що таблиця закінчилась, — дамп тихо недочитав би решту.
    Для бекапу це найгірший клас помилки: файл виглядає нормальним, а даних у
    ньому немає. Ціна такої умови — один зайвий (порожній) запит у кінці.
    """
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
        if not batch:
            return rows
        rows.extend(batch)


def build_dump() -> dict:
    """Повний дамп усіх таблиць із БД."""
    tables = {name: _fetch_table(name, order) for name, order in BACKUP_TABLES.items()}
    return {
        "created_at": datetime.now(KYIV_TZ).isoformat(),
        "counts": {name: len(rows) for name, rows in tables.items()},
        "tables": tables,
    }
