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


def get_staff(company_id: str) -> list[dict]:
    """Список майстрів, доступних для онлайн-запису."""
    return _request("GET", f"book_staff/{company_id}")["data"]


def get_available_dates(company_id: str, staff_id: int = None, service_ids: list[int] = None) -> list[str]:
    """Дати з вільними слотами (staff_id=0 — будь-який майстер)."""
    params = {}
    if service_ids:
        params["service_ids[]"] = service_ids
    path = f"book_dates/{company_id}"
    if staff_id:
        path = f"book_dates/{company_id}"
        params["staff_id"] = staff_id
    return _request("GET", path, params=params)["data"]["booking_dates"]


def get_available_times(company_id: str, staff_id: int, date: str) -> list[dict]:
    """Вільні часи на конкретну дату (date у форматі YYYY-MM-DD)."""
    return _request("GET", f"book_times/{company_id}/{staff_id}/{date}")["data"]


# --- Клієнти ---

def find_client_by_phone(company_id: str, phone: str) -> dict | None:
    """Пошук клієнта за номером телефону. Повертає None, якщо не знайдено."""
    data = _request("GET", f"clients/{company_id}", params={"phone": phone})["data"]
    return data[0] if data else None


def create_client(company_id: str, name: str, phone: str) -> dict:
    """Створити нового клієнта в Altegio."""
    payload = {"name": name, "phone": phone}
    return _request("POST", f"clients/{company_id}", json=payload)["data"]


# --- Записи ---

def get_client_records(company_id: str, client_id: int) -> list[dict]:
    """Список записів клієнта (минулі й майбутні)."""
    return _request("GET", f"records/{company_id}", params={"client_id": client_id})["data"]


def create_record(company_id: str, client_id: int, staff_id: int, service_id: int,
                   datetime_str: str, comment: str = "") -> dict:
    """Створити запис. datetime_str у форматі 'YYYY-MM-DD HH:MM:SS'."""
    payload = {
        "staff_id": staff_id,
        "services": [{"id": service_id}],
        "client": {"id": client_id},
        "datetime": datetime_str,
        "comment": comment,
    }
    return _request("POST", f"records/{company_id}", json=payload)["data"]


def move_record(company_id: str, record_id: int, staff_id: int, datetime_str: str) -> dict:
    """Перенести запис на інший час/майстра."""
    payload = {"staff_id": staff_id, "datetime": datetime_str}
    return _request("PUT", f"record/{company_id}/{record_id}", json=payload)["data"]


def cancel_record(company_id: str, record_id: int) -> None:
    """Скасувати запис."""
    _request("DELETE", f"record/{company_id}/{record_id}")