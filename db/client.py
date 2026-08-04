"""Клієнт Supabase. Всі звернення до локальної БД йдуть через цей модуль."""
from datetime import datetime, timezone

from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_client_by_tg_id(tg_user_id: int) -> dict | None:
    """Знайти клієнта за Telegram user_id. Повертає None, якщо не знайдено."""
    result = supabase.table("clients").select("*").eq("tg_user_id", tg_user_id).limit(1).execute()
    return result.data[0] if result.data else None


def create_client_record(tg_user_id: int) -> dict:
    """Створити порожній запис клієнта (реєстрацію заповнюємо покроково)."""
    result = supabase.table("clients").insert({"tg_user_id": tg_user_id}).execute()
    return result.data[0]


def update_client(client_id: int, fields: dict) -> dict:
    """Оновити поля клієнта."""
    result = supabase.table("clients").update(fields).eq("id", client_id).execute()
    return result.data[0]


def get_client_by_id(client_id: int) -> dict | None:
    """Знайти клієнта за внутрішнім id."""
    result = supabase.table("clients").select("*").eq("id", client_id).limit(1).execute()
    return result.data[0] if result.data else None


def get_client_by_phone(phone: str) -> dict | None:
    """Знайти клієнта за телефоном (формат +380XXXXXXXXX). Для матчингу Altegio-вебхуків."""
    result = supabase.table("clients").select("*").eq("phone", phone).limit(1).execute()
    return result.data[0] if result.data else None


def get_clients_with_altegio_link() -> list[dict]:
    """Клієнти, прив'язані до Altegio (для щоденної синхронізації вакцинації, Фаза 10)."""
    result = (
        supabase.table("clients")
        .select("*")
        .not_.is_("altegio_client_id", "null")
        .not_.is_("altegio_company_id", "null")
        .execute()
    )
    return result.data


# --- Улюбленці ---

def create_pet(client_id: int, fields: dict) -> dict:
    """Створити картку улюбленця."""
    result = supabase.table("pets").insert({"client_id": client_id, **fields}).execute()
    return result.data[0]


def get_pets_by_client(client_id: int) -> list[dict]:
    """Всі улюбленці клієнта."""
    result = supabase.table("pets").select("*").eq("client_id", client_id).order("id").execute()
    return result.data


def get_pet(pet_id: int) -> dict | None:
    """Картка улюбленця за id."""
    result = supabase.table("pets").select("*").eq("id", pet_id).limit(1).execute()
    return result.data[0] if result.data else None


def update_pet(pet_id: int, fields: dict) -> dict:
    """Оновити поля улюбленця."""
    result = supabase.table("pets").update(fields).eq("id", pet_id).execute()
    return result.data[0]


def delete_pet(pet_id: int) -> None:
    """Видалити картку улюбленця."""
    supabase.table("pets").delete().eq("id", pet_id).execute()


def get_pets_with_birth_date() -> list[dict]:
    """Усі улюбленці з відомою датою народження (щоденна перевірка днів народження, Фаза 7).

    PostgREST не фільтрує по місяцю/дню напряму - зіставлення з "сьогодні"
    робиться в Python (services/birthday.py), масштаб (кілька філій) це дозволяє.
    """
    result = supabase.table("pets").select("id, client_id, name, birth_date").not_.is_("birth_date", "null").execute()
    return result.data


# --- Записи (кеш для нагадувань, Фаза 2+) ---

def get_tracked_record(altegio_record_id: int) -> dict | None:
    """Кешований запис за id з Altegio. None, якщо ще не синхронізований."""
    result = (
        supabase.table("tracked_records")
        .select("*")
        .eq("altegio_record_id", altegio_record_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def upsert_tracked_record(fields: dict) -> dict:
    """Створити або оновити кеш запису (fields повинні містити altegio_record_id)."""
    result = supabase.table("tracked_records").upsert(fields, on_conflict="altegio_record_id").execute()
    return result.data[0]


def update_tracked_record_status(altegio_record_id: int, status: str) -> None:
    """Позначити статус запису (напр. cancelled при скасуванні в Altegio)."""
    supabase.table("tracked_records").update({"status": status}).eq(
        "altegio_record_id", altegio_record_id
    ).execute()


def get_tracked_record_by_id(record_id: int) -> dict | None:
    """Кешований запис за внутрішнім id (дії клієнта: перенос/скасування)."""
    result = supabase.table("tracked_records").select("*").eq("id", record_id).limit(1).execute()
    return result.data[0] if result.data else None


def get_upcoming_tracked_records(client_id: int) -> list[dict]:
    """Майбутні активні записи клієнта, найближчі першими."""
    now = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("tracked_records")
        .select("*")
        .eq("client_id", client_id)
        .eq("status", "active")
        .gte("starts_at", now)
        .order("starts_at")
        .execute()
    )
    return result.data


def get_active_tracked_records_in_range(company_id: str, start: str, end: str) -> list[dict]:
    """Активні записи філії в межах вікна дат (для щоденної звірки: скасовані в Altegio
    записи повністю зникають з відповіді get_records(), тому пропущене скасування
    ловиться лише порівнянням "що в нас active" з "що повернула Altegio")."""
    result = (
        supabase.table("tracked_records")
        .select("*")
        .eq("company_id", company_id)
        .eq("status", "active")
        .gte("starts_at", start)
        .lte("starts_at", end)
        .execute()
    )
    return result.data


def get_active_tracked_records_with_ends_at() -> list[dict]:
    """Активні записи з відомим ends_at (перевірка прострочених rebook, Фаза 7).

    Без фільтра по даті - tracked_records кешує лише записи, зроблені через
    бота/вебхук (не всю історію Altegio), тому масштаб невеликий; вибір
    "останнього запису клієнта" і "прострочено 6+ тижнів" - у Python
    (services/rebook_promo.py).
    """
    result = (
        supabase.table("tracked_records")
        .select("altegio_record_id, client_id, company_id, location_title, ends_at")
        .eq("status", "active")
        .not_.is_("ends_at", "null")
        .execute()
    )
    return result.data


def has_tracked_record_since(client_id: int, since: str) -> bool:
    """Чи з'явився активний запис клієнта після вказаного часу (перевірка, чи флоу запису таки завершили)."""
    result = (
        supabase.table("tracked_records")
        .select("id")
        .eq("client_id", client_id)
        .eq("status", "active")
        .gte("created_at", since)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def get_last_past_tracked_record(client_id: int) -> dict | None:
    """Останній минулий (не скасований) запис клієнта — для «Повторити останній запис»."""
    now = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("tracked_records")
        .select("*")
        .eq("client_id", client_id)
        .eq("status", "active")
        .lt("starts_at", now)
        .order("starts_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


# --- Сповіщення ---

def create_notification(
    client_id: int, type: str, send_after: str, payload: dict | None = None,
    altegio_record_id: int | None = None,
) -> dict:
    """Запланувати сповіщення (send_after — ISO timestamp)."""
    result = supabase.table("notifications").insert({
        "client_id": client_id,
        "type": type,
        "send_after": send_after,
        "payload_json": payload,
        "altegio_record_id": altegio_record_id,
    }).execute()
    return result.data[0]


def delete_pending_notifications_for_record(altegio_record_id: int, types: list[str]) -> None:
    """Видалити pending-сповіщення заданих типів для конкретного запису (Фаза 4: reminder_2h/thanks_rating)."""
    supabase.table("notifications").delete().eq("altegio_record_id", altegio_record_id).eq(
        "status", "pending"
    ).in_("type", types).execute()


def has_pending_notification(client_id: int, type: str) -> bool:
    """Чи є вже заплановане (pending) сповіщення цього типу для клієнта."""
    result = (
        supabase.table("notifications")
        .select("id")
        .eq("client_id", client_id)
        .eq("type", type)
        .eq("status", "pending")
        .limit(1)
        .execute()
    )
    return bool(result.data)


def mark_notification(notification_id: int, status: str) -> None:
    """Позначити сповіщення як sent/failed."""
    fields = {"status": status}
    if status == "sent":
        fields["sent_at"] = datetime.now(timezone.utc).isoformat()
    supabase.table("notifications").update(fields).eq("id", notification_id).execute()


# --- Оцінки (Фаза 4, частина 2) ---

def create_rating(altegio_record_id: int, service_stars: int | None, groomer_stars: int) -> dict:
    """Записати оцінку послуги/грумера для завершеного візиту."""
    result = supabase.table("ratings").insert({
        "altegio_record_id": altegio_record_id,
        "service_stars": service_stars,
        "groomer_stars": groomer_stars,
    }).execute()
    return result.data[0]


def get_rating(altegio_record_id: int) -> dict | None:
    """Оцінка запису, якщо вже поставлена (захист від подвійного тапу)."""
    result = supabase.table("ratings").select("*").eq("altegio_record_id", altegio_record_id).limit(1).execute()
    return result.data[0] if result.data else None


# --- Щоденні (не 10-хвилинні) cron-задачі ---

def get_cron_last_run(key: str) -> str | None:
    """Дата (ISO) останнього запуску щоденної задачі з цим ключем. None, якщо ще не запускалась."""
    result = supabase.table("cron_state").select("last_run_date").eq("key", key).limit(1).execute()
    return result.data[0]["last_run_date"] if result.data else None


def set_cron_last_run(key: str, last_run_date: str) -> None:
    """Позначити, що щоденна задача виконана сьогодні (ISO-дата)."""
    supabase.table("cron_state").upsert({"key": key, "last_run_date": last_run_date}, on_conflict="key").execute()