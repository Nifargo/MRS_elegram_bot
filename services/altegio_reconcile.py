"""Щоденна звірка записів Altegio з локальним кешем tracked_records.

Вебхуки (services/altegio_webhook.py) — основний шлях, але не гарантований
(Altegio не підтверджує документацією надійність доставки, PythonAnywhere
проксі інколи губить вхідні запити). Ця звірка підхоплює пропущені
створення/переноси/скасування, перебираючи майбутні записи всіх філій і
проганяючи їх через ту саму process_record(), що й вебхук — жодної окремої
логіки звірки, лише інший вхід у той самий ідемпотентний шлях.
"""
import logging

from config import ALTEGIO_LOCATIONS
from datetime import datetime, timedelta

from db import client as db
from services import altegio, notifications
from services.altegio_webhook import process_record
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

RECONCILE_WINDOW_DAYS = 3


def reconcile_upcoming_records() -> bool:
    """Пройтись по всіх філіях і звірити записи на найближчі RECONCILE_WINDOW_DAYS днів.

    Повертає True лише якщо жодна філія не впала з помилкою (той самий контракт,
    що vaccine_sync.sync_vaccine_dates() — часткова невдача не позначає день як
    зроблений, щоб наступний тик /cron того ж дня повторив спробу).
    """
    today = datetime.now(KYIV_TZ).date()
    start_date = today.isoformat()
    end_date = (today + timedelta(days=RECONCILE_WINDOW_DAYS)).isoformat()
    # Межі того самого вікна у форматі, що зберігається в tracked_records.starts_at
    # (isoformat з тим самим +offset — рядкове gte/lte в get_active_tracked_records_in_range
    # коректне, доки offset однаковий для всіх записів, як і є в цьому проєкті).
    window_start = datetime.combine(today, datetime.min.time(), tzinfo=KYIV_TZ).isoformat()
    window_end = datetime.combine(today + timedelta(days=RECONCILE_WINDOW_DAYS), datetime.min.time(), tzinfo=KYIV_TZ).isoformat()

    all_ok = True
    for location_name, company_id in ALTEGIO_LOCATIONS.items():
        try:
            records = altegio.get_records(company_id, start_date, end_date)
        except Exception as e:
            logger.error(f"Altegio reconcile: помилка отримання записів філії {location_name}: {e}", exc_info=True)
            all_ok = False
            continue

        seen_ids = set()
        for record in records:
            seen_ids.add(record.get("id"))
            try:
                process_record(record, company_id)
            except Exception as e:
                record_id = record.get("id")
                logger.error(f"Altegio reconcile: помилка обробки запису {record_id} ({location_name}): {e}", exc_info=True)
                all_ok = False

        # Altegio повністю прибирає скасовані записи зі списку get_records() (не
        # позначає attendance/deleted, як у вебхуку) - тому пропущене скасування
        # ловимо лише порівнянням: локально "active" в цьому вікні, але Altegio
        # більше про нього не знає.
        try:
            local_active = db.get_active_tracked_records_in_range(company_id, window_start, window_end)
        except Exception as e:
            logger.error(f"Altegio reconcile: помилка читання локального кешу філії {location_name}: {e}", exc_info=True)
            all_ok = False
            continue

        for local_record in local_active:
            record_id = local_record["altegio_record_id"]
            if record_id in seen_ids:
                continue
            try:
                db.update_tracked_record_status(record_id, "cancelled")
                notifications.cancel_visit_notifications(record_id)
                logger.info(f"Altegio reconcile: запис {record_id} ({location_name}) зник з Altegio - позначено cancelled")
            except Exception as e:
                logger.error(f"Altegio reconcile: помилка скасування зниклого запису {record_id} ({location_name}): {e}", exc_info=True)
                all_ok = False

    return all_ok
