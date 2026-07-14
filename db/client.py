"""Клієнт Supabase. Всі звернення до локальної БД йдуть через цей модуль."""
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