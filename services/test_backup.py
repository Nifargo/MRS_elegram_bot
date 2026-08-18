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
            MagicMock(data=[]),
        ]

        dump = backup.build_dump()

        self.assertEqual(dump["counts"], {"clients": 3})
        self.assertEqual(len(dump["tables"]["clients"]), 3)
        # Кожна сторінка зсувається на фактично отримані рядки (0 → 2 → 3), а не
        # на номер сторінки × PAGE_SIZE; останній запит порожній — це умова виходу.
        self.assertEqual(
            [c.args for c in range_call.call_args_list], [(0, 1), (2, 3), (3, 4)]
        )

    @patch("services.backup.BACKUP_TABLES", {"clients": "id"})
    @patch("services.backup.PAGE_SIZE", 10)
    @patch("services.backup.supabase")
    def test_reads_all_pages_when_server_limit_is_below_page_size(self, supabase):
        """Сервер віддає менше, ніж PAGE_SIZE: дамп усе одно повний."""
        self._range_call(supabase).return_value.execute.side_effect = [
            MagicMock(data=[{"id": 1}, {"id": 2}]),
            MagicMock(data=[{"id": 3}, {"id": 4}]),
            MagicMock(data=[]),
        ]

        dump = backup.build_dump()

        self.assertEqual(dump["counts"], {"clients": 4})
        self.assertEqual(len(dump["tables"]["clients"]), 4)

    @patch("services.backup.BACKUP_TABLES", {"cron_state": "key"})
    @patch("services.backup.supabase")
    def test_sorts_by_declared_column(self, supabase):
        self._range_call(supabase).return_value.execute.return_value = MagicMock(data=[])

        backup.build_dump()

        order_call = supabase.table.return_value.select.return_value.order
        self.assertEqual(order_call.call_args.args, ("key",))


if __name__ == "__main__":
    unittest.main()
