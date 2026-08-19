"""Тижневий бекап: склад дампа, сторінкове читання, гейтування по тижню, відправка."""
import unittest
from datetime import date, datetime
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


class BackupDueTest(unittest.TestCase):
    """Субота — штатний день; неділя — підхват, якщо cron проспав суботу."""

    def test_due_on_saturday_after_hour(self):
        now = datetime(2026, 8, 22, 7, 5, tzinfo=backup.KYIV_TZ)  # субота
        self.assertTrue(backup.is_backup_due(now, None, None))

    def test_not_due_before_hour(self):
        now = datetime(2026, 8, 22, 6, 59, tzinfo=backup.KYIV_TZ)
        self.assertFalse(backup.is_backup_due(now, None, None))

    def test_not_due_on_weekday(self):
        now = datetime(2026, 8, 19, 12, 0, tzinfo=backup.KYIV_TZ)  # середа
        self.assertFalse(backup.is_backup_due(now, None, None))

    def test_not_due_twice_in_same_week(self):
        now = datetime(2026, 8, 22, 9, 0, tzinfo=backup.KYIV_TZ)
        # last_attempt=None навмисно: інакше рішення обірветься на позначці
        # спроби і тижневої позначки взагалі не перевірить.
        self.assertFalse(backup.is_backup_due(now, "2026-08-22", None))

    def test_sunday_catches_up_missed_saturday(self):
        now = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)  # неділя
        self.assertTrue(backup.is_backup_due(now, None, None))

    def test_sunday_skipped_when_saturday_done(self):
        now = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)
        self.assertFalse(backup.is_backup_due(now, "2026-08-22", "2026-08-22"))

    def test_due_again_next_week(self):
        now = datetime(2026, 8, 29, 7, 0, tzinfo=backup.KYIV_TZ)  # наступна субота
        self.assertTrue(backup.is_backup_due(now, "2026-08-22", "2026-08-22"))

    def test_not_due_twice_in_same_day_after_failed_attempt(self):
        """Стійкий збій дає одну спробу на добу, а не одну на кожен тик cron.

        Позначка успіху при збої не ставиться, а зовнішній cron стукає кожні
        ~10 хвилин: без окремої позначки спроби гілка зібрала б повний дамп і
        сповістила адмінів ~246 разів за вихідні.
        """
        saturday = datetime(2026, 8, 22, 9, 0, tzinfo=backup.KYIV_TZ)
        sunday = datetime(2026, 8, 23, 9, 0, tzinfo=backup.KYIV_TZ)
        self.assertFalse(backup.is_backup_due(saturday, None, "2026-08-22"))
        self.assertFalse(backup.is_backup_due(sunday, None, "2026-08-23"))

    def test_sunday_retries_after_failed_saturday_attempt(self):
        """Підхват у неділю живий: позначка спроби добова, а не тижнева."""
        now = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)  # неділя
        self.assertTrue(backup.is_backup_due(now, None, "2026-08-22"))

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
        # Мовчазна відмова має лишати слід у логах, інакше незадана змінна
        # виглядає як «бекап працює». assertLogs заразом тримає вивід тестів
        # чистим.
        with self.assertLogs("services.backup", "WARNING"):
            result = backup.send_weekly_backup()

        self.assertFalse(result)
        notifications.send_telegram_document.assert_not_called()
        build_dump.assert_not_called()

    @patch("services.backup.BACKUP_CHAT_ID", None)
    @patch("services.backup.notifications")
    @patch("services.backup.build_dump")
    def test_missing_chat_id_notifies_admins(self, build_dump, notifications):
        """Незадана змінна — найімовірніший збій у проді, тож не лише в лог.

        `BACKUP_CHAT_ID` додається в оточення PythonAnywhere руками, і рядок у
        лозі ніхто не читає — зовні «нема бекапу» не відрізнити від «бекап
        працює». Адмін-група налаштована окремою змінною, тож цей канал живий
        саме тоді, коли `BACKUP_CHAT_ID` немає.
        """
        with self.assertLogs("services.backup", "WARNING"):
            backup.send_weekly_backup()

        notifications.notify_admins.assert_called_once()

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
        # Порожня таблиця лишається в підписі: `ratings: 0` — це або норма, або
        # тривога (закрились права, таблицю перейменувала міграція, помилковий
        # delete), а зникнення рядка не помітно ніяк. Підпис — єдиний артефакт,
        # який власник читає, не відкриваючи файл.
        self.assertIn("ratings: 0", args.kwargs["caption"])
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

        with self.assertLogs("services.backup", "ERROR"):
            result = backup.send_weekly_backup()

        self.assertFalse(result)
        notifications.send_telegram_document.assert_not_called()
        notifications.notify_admins.assert_called_once()


class SchedulerWiringTest(unittest.TestCase):
    """Гілка в _run_daily_tasks(): бекап викликається і позначається датою суботи."""

    @staticmethod
    def _stub_backup(mock_backup):
        """Ключі cron_state — справжні рядки, інакше в позначки летять моки."""
        mock_backup.BACKUP_KEY = "backup"
        mock_backup.BACKUP_ATTEMPT_KEY = "backup_attempt"
        mock_backup.saturday_of_week.return_value = date(2026, 8, 22)

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
        self._stub_backup(mock_backup)

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
        self._stub_backup(mock_backup)

        scheduler._run_daily_tasks()

        calls = [c.args for c in db.set_cron_last_run.call_args_list]
        self.assertNotIn(("backup", "2026-08-22"), calls)

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_sunday_run_marks_saturday_of_week_not_today(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        """Підхват у неділю позначає суботу — інакше каденція стала б добовою.

        Тест саме на неділю: у суботу `today` і субота тижня — та сама дата, тож
        помилкове `today` в позначці лишилось би непоміченим.
        """
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)
        db.get_cron_last_run.return_value = None
        mock_backup.is_backup_due.return_value = True
        mock_backup.send_weekly_backup.return_value = True
        self._stub_backup(mock_backup)

        scheduler._run_daily_tasks()

        db.set_cron_last_run.assert_any_call("backup", "2026-08-22")
        calls = [c.args for c in db.set_cron_last_run.call_args_list]
        self.assertNotIn(("backup", "2026-08-23"), calls)
        self.assertEqual(mock_backup.saturday_of_week.call_args.args, (date(2026, 8, 23),))

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_decision_gets_kyiv_now_and_both_marks(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        """`is_backup_due()` отримує київський `now` і обидві позначки в правильному порядку.

        Наївний або UTC-час тихо зсунув би поріг 7:00, читання позначки не тим
        ключем зробило б тижневу каденцію залежною від чужої задачі, а переплутані
        між собою позначки успіху й спроби зламали б каденцію в обидва боки.
        """
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 22, 7, 30, tzinfo=backup.KYIV_TZ)
        marks = {"backup": "2026-08-15", "backup_attempt": "2026-08-16"}
        db.get_cron_last_run.side_effect = lambda key: marks.get(key)
        mock_backup.is_backup_due.return_value = True
        mock_backup.send_weekly_backup.return_value = True
        self._stub_backup(mock_backup)

        scheduler._run_daily_tasks()

        mock_datetime.now.assert_called_once_with(scheduler.KYIV_TZ)
        self.assertIs(mock_backup.is_backup_due.call_args.args[0], mock_datetime.now.return_value)
        self.assertEqual(mock_backup.is_backup_due.call_args.args[1], "2026-08-15")
        self.assertEqual(mock_backup.is_backup_due.call_args.args[2], "2026-08-16")

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_not_due_skips_backup(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        """У будній день (рішення — за backup.is_backup_due()) дамп не збирається."""
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 19, 12, 0, tzinfo=backup.KYIV_TZ)
        db.get_cron_last_run.return_value = None
        mock_backup.is_backup_due.return_value = False
        self._stub_backup(mock_backup)

        scheduler._run_daily_tasks()

        mock_backup.send_weekly_backup.assert_not_called()
        keys = [key for key, *_ in (c.args for c in db.set_cron_last_run.call_args_list)]
        self.assertNotIn("backup", keys)
        self.assertNotIn("backup_attempt", keys)

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_backup_exception_does_not_mark_week_done(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 22, 7, 30, tzinfo=backup.KYIV_TZ)
        db.get_cron_last_run.return_value = None
        mock_backup.is_backup_due.return_value = True
        mock_backup.send_weekly_backup.side_effect = RuntimeError("Supabase недоступний")
        self._stub_backup(mock_backup)

        with self.assertLogs("services.scheduler", "ERROR"):
            scheduler._run_daily_tasks()

        calls = [c.args for c in db.set_cron_last_run.call_args_list]
        self.assertNotIn(("backup", "2026-08-22"), calls)

    @patch("services.scheduler.rebook_promo")
    @patch("services.scheduler.birthday")
    @patch("services.scheduler.vaccine_sync")
    @patch("services.scheduler.altegio_reconcile")
    @patch("services.scheduler.backup")
    @patch("services.scheduler.db")
    @patch("services.scheduler.datetime")
    def test_attempt_is_marked_before_run_with_today(
        self, mock_datetime, db, mock_backup, *_others,
    ):
        """Позначка спроби ставиться ДО дампа і сьогоднішньою датою.

        Порядок принциповий: якби позначка йшла після, то падіння дампа (виняток
        або таймаут Supabase) лишило б добу непозначеною, і наступний тик через
        10 хвилин почав би все спочатку. Дата — сьогоднішня, а не суботи тижня,
        інакше неділя-підхват не відрізнялась би від суботньої спроби.
        """
        from services import scheduler

        mock_datetime.now.return_value = datetime(2026, 8, 23, 8, 0, tzinfo=backup.KYIV_TZ)  # неділя
        db.get_cron_last_run.return_value = None
        mock_backup.is_backup_due.return_value = True
        self._stub_backup(mock_backup)

        marks_before_send = []

        def send_and_snapshot_marks():
            marks_before_send.extend(c.args for c in db.set_cron_last_run.call_args_list)
            return False  # збій: позначка успіху не стає, а спроба вже зафіксована

        mock_backup.send_weekly_backup.side_effect = send_and_snapshot_marks

        scheduler._run_daily_tasks()

        self.assertIn(("backup_attempt", "2026-08-23"), marks_before_send)
        calls = [c.args for c in db.set_cron_last_run.call_args_list]
        self.assertNotIn(("backup", "2026-08-22"), calls)


if __name__ == "__main__":
    unittest.main()
