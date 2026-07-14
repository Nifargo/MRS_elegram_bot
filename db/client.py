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


# --- Сповіщення ---

def create_notification(client_id: int, type: str, send_after: str, payload: dict | None = None) -> dict:
    """Запланувати сповіщення (send_after — ISO timestamp)."""
    result = supabase.table("notifications").insert({
        "client_id": client_id,
        "type": type,
        "send_after": send_after,
        "payload_json": payload,
    }).execute()
    return result.data[0]


def mark_notification(notification_id: int, status: str) -> None:
    """Позначити сповіщення як sent/failed."""
    fields = {"status": status}
    if status == "sent":
        fields["sent_at"] = datetime.now(timezone.utc).isoformat()
    supabase.table("notifications").update(fields).eq("id", notification_id).execute()