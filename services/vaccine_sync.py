"""Фаза 10: дата закінчення дії вакцинації — коментар клієнта Altegio → Supabase → нагадування.

Адміністратори вручну пишуть дату в коментар картки клієнта Altegio (довільний
формат дд.мм.рррр) і не пишуть туди жодних інших дат — тож шукаємо першу дату
по всьому тексту коментаря, без прив'язки до маркера блоку бота.
"""
import logging
import re
from datetime import date, datetime

from db import client as db
from services import altegio, notifications
from services.altegio import AltegioError
from services.notifications import KYIV_TZ

logger = logging.getLogger(__name__)

VACCINE_REMINDER_DAYS_BEFORE = 7

_DATE_RE = re.compile(r"(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{2,4})")


def _parse_due_date(comment: str) -> date | None:
    """Перша дата в коментарі клієнта (адміни не пишуть туди інших дат, крім вакцинації)."""
    match = _DATE_RE.search(comment or "")
    if not match:
        return None
    day, month, year = match.groups()
    year = int(year)
    if year < 100:
        year += 2000
    try:
        return date(year, int(month), int(day))
    except ValueError:
        return None


def sync_vaccine_dates() -> int:
    """Оновити vaccine_due_date і надіслати нагадування тим, кому лишилось ≤7 днів.

    "≤7", а не рівно 7: якщо синк пропустить точний день (деплой, збій cron-тика),
    нагадування наздоганяється на наступному запуску, а не губиться назавжди.
    Флаг `vaccine_notified_due_date` захищає від повторного нагадування на ту саму
    дату — спрацьовує знову лише тоді, коли адмін впише нову дату вакцинації.
    """
    clients = db.get_clients_with_altegio_link()
    today = datetime.now(KYIV_TZ).date()
    notified = 0

    for c in clients:
        try:
            remote = altegio.get_client(c["altegio_company_id"], c["altegio_client_id"])
        except AltegioError as e:
            logger.warning(f"Не вдалося прочитати клієнта Altegio (client_id={c['id']}): {e}")
            continue

        due_date = _parse_due_date(remote.get("comment") or "")
        new_due = due_date.isoformat() if due_date else None
        if new_due != c.get("vaccine_due_date"):
            db.update_client(c["id"], {"vaccine_due_date": new_due})
            c = {**c, "vaccine_due_date": new_due}

        if due_date is None or (due_date - today).days > VACCINE_REMINDER_DAYS_BEFORE:
            continue
        if c.get("vaccine_notified_due_date") == new_due:
            continue

        text = "💉 Термін дії вакцинації вашого улюбленця закінчується через 7 днів. Будь ласка, не забудьте ревакцинувати!"
        if notifications.send_telegram_message(c["tg_user_id"], text):
            db.update_client(c["id"], {"vaccine_notified_due_date": new_due})
            notified += 1

    logger.info(f"💉 Синхронізація вакцинації: перевірено {len(clients)}, надіслано нагадувань {notified}")
    return notified
