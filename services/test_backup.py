"""build_dump(): усі таблиці в дампі, великі таблиці читаються сторінками."""
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from services import backup

# Очікуваний склад дампа явним літералом, а не з BACKUP_TABLES: інакше перевірка
# тавтологічна (`tables` будується саме по BACKUP_TABLES) і забута після міграції
# таблиця не зламала б жодного тесту.
EXPECTED_TABLES = {
    "clients",
    "pets",
    "tracked_records",
    "visit_extras",
    "ratings",
    "notifications",
    "chat_messages",
    "cron_state",
}


class BuildDumpTest(unittest.TestCase):
    def _stub_pages(self, supabase, *pages):
        """Ланцюжок supabase.table().select().order().limit()[.gt()] одним моком.

        Кожна ланка повертає той самий об'єкт, тож усі сторінки йдуть через один
        .execute() і задаються послідовністю. Без аргументів — таблиця порожня.
        `spec` обмежує набір ланок: якщо читання повернеться до зсуву (.range()),
        тест впаде, а не пройде тихо.
        """
        query = MagicMock(spec=["select", "order", "limit", "gt", "execute"])
        for link in ("select", "order", "limit", "gt"):
            getattr(query, link).return_value = query
        supabase.table.return_value = query
        if pages:
            query.execute.side_effect = [MagicMock(data=list(page)) for page in pages]
        else:
            query.execute.return_value = MagicMock(data=[])
        return query

    @patch("services.backup.supabase")
    def test_dump_contains_every_table_and_counts(self, supabase):
        self._stub_pages(supabase)

        dump = backup.build_dump()

        self.assertEqual(set(dump["tables"]), EXPECTED_TABLES)
        self.assertEqual(set(dump["counts"]), set(dump["tables"]))

    @patch("services.backup.supabase")
    def test_created_at_is_iso_with_kyiv_offset(self, supabase):
        """Мітка часу — розбірна ISO-дата в київському часі, а не просто рядок."""
        self._stub_pages(supabase)

        created_at = datetime.fromisoformat(backup.build_dump()["created_at"])

        # Не фіксований offset: Київ живе то на +02:00, то на +03:00.
        self.assertEqual(
            created_at.utcoffset(), datetime.now(backup.KYIV_TZ).utcoffset()
        )

    @patch("services.backup.BACKUP_TABLES", {"clients": "id"})
    @patch("services.backup.PAGE_SIZE", 2)
    @patch("services.backup.supabase")
    def test_next_page_starts_after_last_read_key(self, supabase):
        """Наступна сторінка фільтрується по останньому ключу, а не по зсуву.

        Зсув від кількості прочитаного ламається, якщо між двома сторінками
        рядок видаляється (`db/client.py::delete_pet()`,
        `delete_pending_notifications_for_record()` з обробки вебхука Altegio):
        решта рядків зсувається, і один тихо не потрапляє в дамп. Читання
        «від останнього ключа» від видалень не залежить.
        """
        query = self._stub_pages(
            supabase, [{"id": 1}, {"id": 2}], [{"id": 3}, {"id": 4}], []
        )

        dump = backup.build_dump()

        self.assertEqual(dump["counts"], {"clients": 4})
        # Перша сторінка — без .gt(), тобто з початку таблиці; далі — від
        # останнього прочитаного ключа.
        self.assertEqual(
            [c.args for c in query.gt.call_args_list], [("id", 2), ("id", 4)]
        )
        self.assertEqual(
            [c.args for c in query.limit.call_args_list], [(2,), (2,), (2,)]
        )

    @patch("services.backup.BACKUP_TABLES", {"clients": "id"})
    @patch("services.backup.PAGE_SIZE", 2)
    @patch("services.backup.supabase")
    def test_reads_all_pages_when_table_exceeds_page_size(self, supabase):
        query = self._stub_pages(supabase, [{"id": 1}, {"id": 2}], [{"id": 3}], [])

        dump = backup.build_dump()

        self.assertEqual(dump["counts"], {"clients": 3})
        self.assertEqual(len(dump["tables"]["clients"]), 3)
        # Три запити на три сторінки: читання не обірвалось на першій, а
        # останній (порожній) — це умова виходу.
        self.assertEqual(query.execute.call_count, 3)

    @patch("services.backup.BACKUP_TABLES", {"clients": "id"})
    @patch("services.backup.PAGE_SIZE", 10)
    @patch("services.backup.supabase")
    def test_reads_all_pages_when_server_limit_is_below_page_size(self, supabase):
        """Сервер віддає менше, ніж PAGE_SIZE: дамп усе одно повний."""
        self._stub_pages(
            supabase, [{"id": 1}, {"id": 2}], [{"id": 3}, {"id": 4}], []
        )

        dump = backup.build_dump()

        self.assertEqual(dump["counts"], {"clients": 4})
        self.assertEqual(len(dump["tables"]["clients"]), 4)

    @patch("services.backup.BACKUP_TABLES", {"cron_state": "key"})
    @patch("services.backup.supabase")
    def test_sorts_by_declared_column(self, supabase):
        query = self._stub_pages(supabase)

        backup.build_dump()

        self.assertEqual(query.order.call_args.args, ("key",))


if __name__ == "__main__":
    unittest.main()
