"""Обробка вебхуків Altegio (запис створено/змінено/скасовано).

Точна форма payload не підтверджена офіційною документацією (сторінки
Altegio API не віддали приклад), тож парсинг тут навмисно захисний:
.get() всюди, жодного KeyError, сирий payload завжди логується, будь-яка
помилка обробки не повинна валити відповідь 200 (Altegio ретраїть на
не-200 статус).

Очікувана форма (типова для Altegio/YCLIENTS):
{"company_id": ..., "resource": "record", "resource_id": ...,
 "status": "create"/"update"/"delete", "data": {...}}
"""
import logging
from datetime import datetime, timedelta

from config import ALTEGIO_LOCATIONS
from db import client as db
from handlers.common import normalize_phone
from services import notifications
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)


def _location_name(company_id: str) -> str:
    return next((name for name, cid in ALTEGIO_LOCATIONS.items() if cid == company_id), company_id)


def _parse_kyiv(raw) -> datetime | None:
    """Розібрати час з вебхука. Реальні payload віддають наївний рядок ("2026-08-22
    10:00:00") без offset — це вже Київський час, тому наївний результат
    локалізуємо явно (без цього Supabase/PostgREST трактував би його як UTC)."""
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=KYIV_TZ)


def _format_dt(raw) -> str:
    dt = _parse_kyiv(raw)
    return dt.strftime("%d.%m.%Y о %H:%M") if dt else str(raw or "")


def process_event(payload: dict) -> None:
    """Точка входу з webhook_bot.py. Ніколи не кидає виключення назовні."""
    logger.info(f"📥 Altegio webhook payload: {payload}")
    try:
        _handle(payload)
    except Exception as e:
        logger.error(f"Altegio webhook: помилка обробки: {e}", exc_info=True)


def _handle(payload: dict) -> None:
    if payload.get("resource") != "record":
        return

    data = payload.get("data") or {}
    if payload.get("status") == "delete":
        record_id = data.get("id") or payload.get("resource_id")
        if not record_id:
            logger.warning("Altegio webhook: запис без id, пропускаю")
            return
        db.update_tracked_record_status(record_id, "cancelled")
        notifications.cancel_visit_notifications(record_id)
        return

    company_id = str(payload.get("company_id") or data.get("company_id") or "")
    process_record(data, company_id)


def process_record(data: dict, company_id: str) -> None:
    """Обробити один запис Altegio (створення/оновлення/скасування): звірити з
    tracked_records і (пере)запланувати сповіщення. Спільна логіка для вебхука
    (вище) і щоденної звірки (services/altegio_reconcile.py) — той самий
    ідемпотентний шлях, незалежно від того, звідки прийшов запис."""
    record_id = data.get("id")
    if not record_id:
        logger.warning("Altegio: запис без id, пропускаю")
        return

    location_title = _location_name(company_id)
    services = data.get("services") or []
    service_title = (services[0].get("title") if services else None) or data.get("service_title") or ""
    starts_at = data.get("datetime") or data.get("date")
    staff_id = data.get("staff_id") or (data.get("staff") or {}).get("id")
    starts_dt = _parse_kyiv(starts_at)
    duration = data.get("seance_length") or data.get("length")
    ends_dt = starts_dt + timedelta(seconds=duration) if starts_dt and duration else None

    is_cancelled = bool(data.get("deleted")) or data.get("attendance") == -1
    existing = db.get_tracked_record(record_id)
    fields = {
        "altegio_record_id": record_id,
        "starts_at": starts_dt.isoformat() if starts_dt else starts_at,
        "ends_at": ends_dt.isoformat() if ends_dt else None,
        "service_title": service_title,
        "location_title": location_title,
        "status": "cancelled" if is_cancelled else "active",
        "company_id": company_id or None,
        "altegio_service_id": services[0].get("id") if services else None,
        "staff_id": staff_id,
        "raw_json": data,
    }

    if existing:
        # Вже відомий запис (зроблений ботом або раніше синхронізований) —
        # тихо оновлюємо, без повторного пушу підтвердження клієнту.
        client_id = existing.get("client_id")
        fields["client_id"] = client_id
        fields["pet_id"] = existing.get("pet_id")
        db.upsert_tracked_record(fields)
        if is_cancelled:
            notifications.cancel_visit_notifications(record_id)
        elif starts_dt:
            notifications.schedule_visit_notifications(client_id, record_id, starts_dt, ends_dt)
        return

    # Новий запис, якого бот не робив (адміністратор в Altegio, клієнт через
    # зовнішній Altegio-віджет, або пропущений вебхук, підхоплений щоденною
    # звіркою) — шукаємо клієнта по телефону і пушимо підтвердження.
    phone = normalize_phone((data.get("client") or {}).get("phone") or "")
    matched_client = db.get_client_by_phone(phone) if phone else None
    client_id = matched_client["id"] if matched_client else None

    fields["client_id"] = client_id
    # Віджет не передає, якого саме улюбленця обрав клієнт — визначаємо
    # однозначно лише коли в клієнта один улюбленець; інакше «Повторити
    # останній запис» (handlers/my_bookings.py) сам перепитає при потребі.
    pets = db.get_pets_by_client(matched_client["id"]) if matched_client else []
    fields["pet_id"] = pets[0]["id"] if len(pets) == 1 else None
    db.upsert_tracked_record(fields)

    if is_cancelled:
        notifications.cancel_visit_notifications(record_id)
    elif starts_dt:
        notifications.schedule_visit_notifications(client_id, record_id, starts_dt, ends_dt)

    if matched_client and not is_cancelled:
        text = (
            "✅ Вас записано на грумінг!\n"
            f"✂️ {service_title}\n"
            f"📍 {location_title}\n"
            f"📅 {_format_dt(starts_at)}"
        )
        notifications.send_telegram_message(matched_client["tg_user_id"], text)
