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
from datetime import datetime

from config import ALTEGIO_LOCATIONS
from db import client as db
from handlers.common import normalize_phone
from services import notifications

logger = logging.getLogger(__name__)


def _location_name(company_id: str) -> str:
    return next((name for name, cid in ALTEGIO_LOCATIONS.items() if cid == company_id), company_id)


def _format_dt(raw) -> str:
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y о %H:%M")
    except ValueError:
        return str(raw)


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
    record_id = data.get("id") or payload.get("resource_id")
    if not record_id:
        logger.warning("Altegio webhook: запис без id, пропускаю")
        return

    status = payload.get("status")
    if status == "delete" or data.get("deleted"):
        db.update_tracked_record_status(record_id, "cancelled")
        return

    company_id = str(payload.get("company_id") or data.get("company_id") or "")
    location_title = _location_name(company_id)
    services = data.get("services") or []
    service_title = (services[0].get("title") if services else None) or data.get("service_title") or ""
    starts_at = data.get("datetime") or data.get("date")

    existing = db.get_tracked_record(record_id)
    fields = {
        "altegio_record_id": record_id,
        "starts_at": starts_at,
        "service_title": service_title,
        "location_title": location_title,
        "status": "cancelled" if data.get("attendance") == -1 else "active",
        "company_id": company_id or None,
        "altegio_service_id": services[0].get("id") if services else None,
        "raw_json": data,
    }

    if existing:
        # Вже відомий запис (зроблений ботом або раніше синхронізований) —
        # тихо оновлюємо, без повторного пушу підтвердження клієнту.
        fields["client_id"] = existing.get("client_id")
        fields["pet_id"] = existing.get("pet_id")
        db.upsert_tracked_record(fields)
        return

    # Новий запис, якого бот не робив (зроблений адміністратором в Altegio) —
    # шукаємо клієнта по телефону і пушимо підтвердження.
    phone = normalize_phone((data.get("client") or {}).get("phone") or "")
    matched_client = db.get_client_by_phone(phone) if phone else None

    fields["client_id"] = matched_client["id"] if matched_client else None
    fields["pet_id"] = None
    db.upsert_tracked_record(fields)

    if matched_client:
        text = (
            "✅ Вас записано на грумінг!\n"
            f"✂️ {service_title}\n"
            f"📍 {location_title}\n"
            f"📅 {_format_dt(starts_at)}"
        )
        notifications.send_telegram_message(matched_client["tg_user_id"], text)
