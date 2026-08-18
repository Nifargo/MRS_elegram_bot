"""Історія візитів клієнта (Фаза 5) — читається напряму з Altegio.

Altegio лишається єдиним джерелом правди по візитах: `tracked_records` кешує
лише записи бот-епохи і нічого не знає про роки роботи салону до появи бота,
тож для історії він не годиться.

У Altegio картка клієнта своя в кожній філії, тому повна історія збирається
пошуком по телефону в усіх `config.ALTEGIO_LOCATIONS`. Збій однієї філії не
приховує візити з решти (той самий per-branch try/except, що в
`services/rebook_promo.py` і `services/altegio_reconcile.py`); якщо ж не вдалося
жодна — кидаємо AltegioError, щоб handler показав помилку, а не «історія
порожня».
"""
import logging
from datetime import datetime

from config import ALTEGIO_LOCATIONS
from handlers.common import parse_iso_datetime
from services import altegio
from services.altegio import AltegioError
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

NO_SHOW_ATTENDANCE = -1


def _location_name(company_id: str) -> str:
    return next((name for name, cid in ALTEGIO_LOCATIONS.items() if cid == company_id), company_id)


def _parse_visit_dt(raw) -> datetime | None:
    """Час візиту з відповіді Altegio. None, якщо поле відсутнє/нерозбірливе."""
    if not raw:
        return None
    try:
        dt = parse_iso_datetime(raw)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=KYIV_TZ)


def _branch_client_ids(client: dict) -> dict[str, int]:
    """company_id -> altegio_client_id для всіх філій, де клієнт відомий.

    «Домашня» філія (зафіксована при реєстрації) береться без запиту, решта —
    пошуком по телефону.
    """
    ids = {}
    home_company, home_client = client.get("altegio_company_id"), client.get("altegio_client_id")
    if home_company and home_client:
        ids[str(home_company)] = home_client

    phone = client.get("phone")
    if not phone:
        return ids

    for name, company_id in ALTEGIO_LOCATIONS.items():
        if company_id in ids:
            continue
        try:
            found = altegio.find_client_by_phone(company_id, phone)
        except AltegioError as e:
            logger.warning(f"Історія: пошук клієнта у філії {name}: {e}")
            continue
        if found and found.get("id"):
            ids[company_id] = found["id"]
    return ids


def _visit_from_record(record: dict, company_id: str) -> dict | None:
    # Беремо наївний `date`, а не `datetime`: Altegio віддає в `datetime` offset
    # +03:00 навіть для зимових дат, коли Київ у +02:00 (перевірено живими
    # записами січня 2026), тож візит показувався б на годину раніше. `date` —
    # це справжній час на годиннику салону, лишається лише локалізувати його.
    starts_at = _parse_visit_dt(record.get("date") or record.get("datetime"))
    if starts_at is None:
        return None

    services = record.get("services") or []
    return {
        "record_id": record.get("id"),
        "company_id": company_id,
        "starts_at": starts_at,
        "location_title": _location_name(company_id),
        "service_titles": [s["title"] for s in services if s.get("title")],
        "cost": sum((s.get("cost") or 0) for s in services),
        "staff_name": (record.get("staff") or {}).get("name"),
    }


def get_past_visits(client: dict) -> list[dict]:
    """Минулі візити клієнта по всіх філіях, найновіші першими.

    Відфільтровані видалені записи, явні «не прийшов» (attendance == -1) і все,
    що ще не відбулось. Записи без позначки attendance лишаються: адміністратор
    проставляє її не завжди, а приховати через це реальний візит гірше, ніж
    показати запис, на який клієнт не з'явився.
    """
    now = datetime.now(KYIV_TZ)
    branches = _branch_client_ids(client)
    visits, failures = [], 0

    for company_id, altegio_client_id in branches.items():
        try:
            records = altegio.get_client_records(company_id, altegio_client_id)
        except AltegioError as e:
            failures += 1
            logger.warning(f"Історія: записи клієнта {altegio_client_id} у філії {company_id}: {e}")
            continue

        for record in records:
            if record.get("deleted") or record.get("attendance") == NO_SHOW_ATTENDANCE:
                continue
            visit = _visit_from_record(record, company_id)
            if visit and visit["starts_at"] < now:
                visits.append(visit)

    if not visits and failures:
        raise AltegioError(f"історія недоступна: {failures} з {len(branches)} філій не відповіли")

    visits.sort(key=lambda v: v["starts_at"], reverse=True)
    return visits
