"""get_past_visits(): що потрапляє в історію, як зливаються філії і що буває при збоях Altegio."""
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from services import visit_history
from services.altegio import AltegioError
from services.notifications import KYIV_TZ

CLIENT = {"id": 8, "phone": "+380667364924", "altegio_company_id": "783219", "altegio_client_id": 111}

ONE_BRANCH = {"Замарстинівська": "783219"}
TWO_BRANCHES = {"Замарстинівська": "783219", "Тернопільська": "748415"}


def _record(record_id: int, dt: datetime, services: list[dict] | None = None, **extra) -> dict:
    return {
        "id": record_id,
        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
        # Altegio ставить у `datetime` +03:00 незалежно від сезону — як у живих даних.
        "datetime": dt.replace(tzinfo=None).isoformat() + "+03:00",
        "services": services if services is not None else [{"id": 1, "title": "Мальтіпу до 4 кг", "cost": 1500}],
        "staff": {"id": 7, "name": "Топ грумер Вікторія"},
        "deleted": False,
        "attendance": 1,
        **extra,
    }


class VisitHistoryTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(KYIV_TZ)

    @patch.dict(visit_history.ALTEGIO_LOCATIONS, ONE_BRANCH, clear=True)
    @patch("services.visit_history.altegio")
    def test_keeps_only_past_visits_that_happened(self, altegio):
        altegio.get_client_records.return_value = [
            _record(1, self.now - timedelta(days=30)),
            _record(2, self.now + timedelta(days=5)),                     # ще не відбувся
            _record(3, self.now - timedelta(days=10), deleted=True),      # видалений в Altegio
            _record(4, self.now - timedelta(days=20), attendance=-1),     # клієнт не прийшов
            _record(5, self.now - timedelta(days=5), attendance=0),       # адмін не проставив позначку
        ]

        visits = visit_history.get_past_visits(CLIENT)

        self.assertEqual([v["record_id"] for v in visits], [5, 1])

    @patch.dict(visit_history.ALTEGIO_LOCATIONS, ONE_BRANCH, clear=True)
    @patch("services.visit_history.altegio")
    def test_sums_cost_of_all_services_in_visit(self, altegio):
        altegio.get_client_records.return_value = [
            _record(1, self.now - timedelta(days=3), services=[
                {"id": 1, "title": "Шпіц 3-5 кг (гігієна)", "cost": 1350},
                {"id": 2, "title": "Маска для собак до 8 кг", "cost": 350},
            ]),
        ]

        visit = visit_history.get_past_visits(CLIENT)[0]

        self.assertEqual(visit["cost"], 1700)
        self.assertEqual(visit["service_titles"], ["Шпіц 3-5 кг (гігієна)", "Маска для собак до 8 кг"])
        self.assertEqual(visit["staff_name"], "Топ грумер Вікторія")
        self.assertEqual(visit["location_title"], "Замарстинівська")

    @patch.dict(visit_history.ALTEGIO_LOCATIONS, ONE_BRANCH, clear=True)
    @patch("services.visit_history.altegio")
    def test_winter_visit_keeps_salon_wall_clock_time(self, altegio):
        # Altegio віддає +03:00 і в січні, коли Київ у +02:00, тож опора на
        # `datetime` показувала б візит на годину раніше, ніж він був.
        altegio.get_client_records.return_value = [{
            "id": 1,
            "date": "2026-01-06 11:15:00",
            "datetime": "2026-01-06T11:15:00+03:00",
            "services": [{"id": 1, "title": "Мальтіпу до 4 кг", "cost": 1500}],
            "staff": {"id": 7, "name": "Топ грумер Вікторія"},
            "deleted": False,
            "attendance": 1,
        }]

        visit = visit_history.get_past_visits(CLIENT)[0]

        self.assertEqual(visit["starts_at"].astimezone(KYIV_TZ).strftime("%d.%m.%Y %H:%M"), "06.01.2026 11:15")

    @patch.dict(visit_history.ALTEGIO_LOCATIONS, TWO_BRANCHES, clear=True)
    @patch("services.visit_history.altegio")
    def test_merges_branches_newest_first(self, altegio):
        altegio.find_client_by_phone.return_value = {"id": 222}
        altegio.get_client_records.side_effect = lambda company_id, client_id: (
            [_record(1, self.now - timedelta(days=30))] if company_id == "783219"
            else [_record(2, self.now - timedelta(days=3))]
        )

        visits = visit_history.get_past_visits(CLIENT)

        self.assertEqual([v["record_id"] for v in visits], [2, 1])
        self.assertEqual(visits[0]["location_title"], "Тернопільська")
        # «Домашня» філія вже відома з реєстрації — шукаємо по телефону лише решту.
        altegio.find_client_by_phone.assert_called_once_with("748415", CLIENT["phone"])

    @patch.dict(visit_history.ALTEGIO_LOCATIONS, TWO_BRANCHES, clear=True)
    @patch("services.visit_history.altegio")
    def test_one_failing_branch_does_not_hide_the_others(self, altegio):
        altegio.find_client_by_phone.return_value = {"id": 222}

        def records(company_id, client_id):
            if company_id == "783219":
                raise AltegioError("HTTP 500")
            return [_record(2, self.now - timedelta(days=3))]

        altegio.get_client_records.side_effect = records

        visits = visit_history.get_past_visits(CLIENT)

        self.assertEqual([v["record_id"] for v in visits], [2])

    @patch.dict(visit_history.ALTEGIO_LOCATIONS, TWO_BRANCHES, clear=True)
    @patch("services.visit_history.altegio")
    def test_raises_when_no_branch_answered(self, altegio):
        altegio.find_client_by_phone.return_value = {"id": 222}
        altegio.get_client_records.side_effect = AltegioError("HTTP 500")

        # Порожній список тут означав би «візитів не було» — клієнту показали б
        # хибне «історія порожня» замість помилки.
        with self.assertRaises(AltegioError):
            visit_history.get_past_visits(CLIENT)


if __name__ == "__main__":
    unittest.main()
