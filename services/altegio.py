"""Клієнт Altegio API (online booking + business management)."""
import logging

import requests

from config import ALTEGIO_PARTNER_TOKEN, ALTEGIO_USER_TOKEN

logger = logging.getLogger(__name__)

BASE_URL = "https://api.alteg.io/api/v1"


class AltegioError(Exception):
    """Помилка звернення до Altegio API."""


def _request(method: str, path: str, params: dict = None, json: dict = None) -> dict:
    url = f"{BASE_URL}/{path}"
    headers = {
        "Authorization": f"Bearer {ALTEGIO_PARTNER_TOKEN}, User {ALTEGIO_USER_TOKEN}",
        "Accept": "application/vnd.api.v2+json",
        "Content-Type": "application/json",
    }

    response = requests.request(method, url, headers=headers, params=params, json=json, timeout=15)

    if not response.ok:
        logger.error(f"Altegio API помилка {response.status_code}: {response.text[:300]}")
        raise AltegioError(f"{method} {path} -> HTTP {response.status_code}: {response.text[:300]}")

    if not response.text.strip():
        # DELETE (cancel_record) інколи повертає успіх із порожнім тілом.
        return {}

    data = response.json()
    if isinstance(data, dict) and data.get("success") is False:
        logger.error(f"Altegio API success=False: {data}")
        raise AltegioError(f"{method} {path} -> {data.get('meta')}")

    return data


# --- Компанія / локації ---

def get_company(company_id: str) -> dict:
    """Інформація про філію (назва, адреса, координати)."""
    return _request("GET", f"company/{company_id}")["data"]


# --- Послуги та вільний час (Online Booking) ---

def get_services(company_id: str) -> list[dict]:
    """Список послуг, доступних для онлайн-запису."""
    return _request("GET", f"book_services/{company_id}")["data"]["services"]


def get_staff(company_id: str, service_ids: list[int] = None) -> list[dict]:
    """Список майстрів, доступних для онлайн-запису (опційно — лише кваліфіковані на service_ids)."""
    params = {"service_ids[]": service_ids} if service_ids else None
    return _request("GET", f"book_staff/{company_id}", params=params)["data"]


def get_service_categories(company_id: str) -> list[dict]:
    """Категорії послуг (тип послуги × рівень грумера), кожна з полем staff (id майстрів)."""
    return _request("GET", f"service_categories/{company_id}")["data"]


def get_available_dates(company_id: str, staff_id: int = None, service_ids: list[int] = None) -> list[str]:
    """Дати з вільними слотами (staff_id=0 — об'єднана доступність по всіх майстрах)."""
    params = {}
    if service_ids:
        params["service_ids[]"] = service_ids
    if staff_id is not None:
        params["staff_id"] = staff_id
    return _request("GET", f"book_dates/{company_id}", params=params)["data"]["booking_dates"]


def get_available_times(company_id: str, staff_id: int, date: str, service_ids: list[int] = None) -> list[dict]:
    """Вільні часи на конкретну дату (date у форматі YYYY-MM-DD).

    service_ids обов'язково впливає на тривалість слотів — без нього повертаються
    часи для іншої (дефолтної) послуги.
    """
    params = {"service_ids[]": service_ids} if service_ids else None
    return _request("GET", f"book_times/{company_id}/{staff_id}/{date}", params=params)["data"]


def find_available_staff_for_slot(company_id: str, service_id: int, date: str, time_str: str) -> tuple[int, int] | None:
    """Знайти конкретного майстра, у якого вільний саме цей час (для create_record —

    там staff_id=0 не підтверджений документацією, тож на підтвердженні запису
    резолвимо «будь-якого майстра» у конкретного, перебираючи кваліфікованих.
    Повертає (staff_id, seance_length) — book_times віддає тривалість слоту в секундах,
    а create_record вимагає її окремим обов'язковим параметром.
    """
    staff = get_staff(company_id, service_ids=[service_id])
    for member in staff:
        times = get_available_times(company_id, member["id"], date, service_ids=[service_id])
        slot = next((t for t in times if t["time"] == time_str), None)
        if slot:
            return member["id"], slot["seance_length"]
    return None


# --- Клієнти ---

def find_client_by_phone(company_id: str, phone: str) -> dict | None:
    """Пошук клієнта за номером телефону. Повертає None, якщо не знайдено."""
    data = _request("GET", f"clients/{company_id}", params={"phone": phone})["data"]
    return data[0] if data else None


def create_client(company_id: str, name: str, phone: str) -> dict:
    """Створити нового клієнта в Altegio."""
    payload = {"name": name, "phone": phone}
    return _request("POST", f"clients/{company_id}", json=payload)["data"]


def get_client(company_id: str, client_id: int) -> dict:
    """Дані клієнта Altegio за id (name, phone, comment, ...)."""
    return _request("GET", f"client/{company_id}/{client_id}")["data"]


def update_client(company_id: str, client_id: int, fields: dict) -> dict:
    """Оновити поля клієнта в Altegio (name, phone, comment, ...)."""
    return _request("PUT", f"client/{company_id}/{client_id}", json=fields)["data"]


# --- Записи ---

def get_client_records(company_id: str, client_id: int) -> list[dict]:
    """Список записів клієнта (минулі й майбутні)."""
    return _request("GET", f"records/{company_id}", params={"client_id": client_id})["data"]


def create_record(company_id: str, client_id: int, staff_id: int, service_id: int,
                   datetime_str: str, seance_length: int, comment: str = "") -> dict:
    """Створити запис. datetime_str у форматі 'YYYY-MM-DD HH:MM:SS'."""
    payload = {
        "staff_id": staff_id,
        "services": [{"id": service_id}],
        "client": {"id": client_id},
        "datetime": datetime_str,
        "seance_length": seance_length,
        "comment": comment,
    }
    return _request("POST", f"records/{company_id}", json=payload)["data"]


def move_record(company_id: str, record_id: int, staff_id: int, client_id: int, service_id: int,
                 datetime_str: str, seance_length: int) -> dict:
    """Перенести запис на інший час/майстра.

    Altegio вимагає той самий повний payload, що й create_record (client/services/
    seance_length) — самого staff_id+datetime недостатньо, перевірено живим тестом (422).
    """
    payload = {
        "staff_id": staff_id,
        "client": {"id": client_id},
        "services": [{"id": service_id}],
        "datetime": datetime_str,
        "seance_length": seance_length,
    }
    return _request("PUT", f"record/{company_id}/{record_id}", json=payload)["data"]


def cancel_record(company_id: str, record_id: int) -> None:
    """Скасувати запис."""
    _request("DELETE", f"record/{company_id}/{record_id}")