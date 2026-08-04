"""Фаза 7, п.3: "Маємо вікно завтра" — щоденна перевірка вільних місць для
клієнтів з простроченим rebook (останній активний запис завершився
REBOOK_DEFAULT_WEEKS+ тижнів тому, і відтоді немає новішого).

Анти-спам через clients.last_promo_at (не частіше раз на 7 днів) природно дає
ефект "раз на тиждень" без прив'язки до конкретного дня — щодня перевіряємо
"є місце завтра" по локації клієнта, і як тільки воно з'являється, шлемо
промо і чекаємо кулдаун. Явне "❌ Скасувати нагадування" (handlers/rebook_promo.py)
глушить конкретно цей прострочений візит (rebook_promo_dismissed_record_id) —
після НОВОГО візиту клієнта "останній запис" зміниться і лічильник 6 тижнів
стартує заново, нагадування відновляться самі.
"""
import logging

from datetime import datetime, timedelta

from config import ALTEGIO_BOOKING_WIDGET_URL
from db import client as db
from services import altegio, notifications
from services.altegio import AltegioError
from services.notifications import KYIV_TZ, REBOOK_DEFAULT_WEEKS

logger = logging.getLogger(__name__)

PROMO_COOLDOWN_DAYS = 7


def _latest_per_client(records: list[dict]) -> list[dict]:
    latest: dict[int, dict] = {}
    for r in records:
        current = latest.get(r["client_id"])
        if current is None or r["ends_at"] > current["ends_at"]:
            latest[r["client_id"]] = r
    return list(latest.values())


def send_rebook_promos() -> bool:
    """Повертає True лише якщо жодна філія/клієнт не впали з помилкою (той самий
    контракт, що vaccine_sync.sync_vaccine_dates())."""
    now = datetime.now(KYIV_TZ)
    cutoff = (now - timedelta(weeks=REBOOK_DEFAULT_WEEKS)).isoformat()
    cooldown_edge = (now - timedelta(days=PROMO_COOLDOWN_DAYS)).isoformat()
    tomorrow = (now + timedelta(days=1)).date().isoformat()

    records = db.get_active_tracked_records_with_ends_at()
    overdue = [r for r in _latest_per_client(records) if r["ends_at"] <= cutoff]

    slot_cache: dict[str, set | None] = {}
    sent = 0
    all_ok = True

    for record in overdue:
        try:
            client = db.get_client_by_id(record["client_id"])
        except Exception as e:
            logger.error(f"Rebook promo: помилка читання клієнта client_id={record['client_id']}: {e}", exc_info=True)
            all_ok = False
            continue
        if client is None:
            continue
        if client.get("rebook_promo_dismissed_record_id") == record["altegio_record_id"]:
            continue
        if client.get("last_promo_at") and client["last_promo_at"] > cooldown_edge:
            continue

        company_id = record.get("company_id")
        if not company_id:
            continue
        if company_id not in slot_cache:
            try:
                slot_cache[company_id] = set(altegio.get_available_dates(company_id, staff_id=0))
            except AltegioError as e:
                logger.warning(f"Rebook promo: не вдалося отримати дати філії {company_id}: {e}")
                slot_cache[company_id] = None
                all_ok = False
        dates = slot_cache[company_id]
        if not dates or tomorrow not in dates:
            continue

        record_id = record["altegio_record_id"]
        text = (
            f"🎉 Завтра є вільні місця в {record.get('location_title') or 'нашому салоні'}! "
            "Час записати улюбленця на грумінг 🐾"
        )
        keyboard = {"inline_keyboard": [
            [{"text": "📅 Записатись", "url": ALTEGIO_BOOKING_WIDGET_URL}],
            [
                {"text": "🔔 Нагадати наступного тижня", "callback_data": f"rp_snooze:{record_id}"},
                {"text": "❌ Скасувати нагадування", "callback_data": f"rp_dismiss:{record_id}"},
            ],
        ]}
        if notifications.send_telegram_message(client["tg_user_id"], text, reply_markup=keyboard):
            try:
                db.update_client(client["id"], {"last_promo_at": now.isoformat()})
                sent += 1
            except Exception as e:
                logger.error(f"Rebook promo: не вдалося записати last_promo_at (client_id={client['id']}): {e}", exc_info=True)
                all_ok = False
        else:
            all_ok = False

    logger.info(f"🎉 Промо вільних місць: прострочених {len(overdue)}, надіслано {sent}{'' if all_ok else ' (є збої — повтор на наступному тику)'}")
    return all_ok
