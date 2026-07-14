"""Синхронізація даних улюбленців у картку клієнта Altegio.

Altegio API не має окремих карток тварин (ризик №2 плану), тому ключову
інформацію про улюбленців дублюємо текстом у коментар клієнта — адміністратор
бачить її у своєму звичному інтерфейсі.

Салони працюють 5 років, у давніх клієнтів у коментарях можуть бути нотатки
адміністраторів — їх НЕ перезаписуємо: блок бота відокремлений маркером,
оновлюється тільки він, решта коментаря зберігається як є.
"""
import logging

from db import client as db
from services import altegio
from services.altegio import AltegioError

logger = logging.getLogger(__name__)

# Маркер блоку бота в коментарі клієнта Altegio. Все до маркера — нотатки
# адміністратора, все після — наш блок (перегенеровується при кожній синхронізації).
BOT_BLOCK_MARKER = "=== Улюбленці (Telegram-бот) ==="


def _pet_line(pet: dict) -> str:
    parts = [pet["name"]]
    if pet.get("breed"):
        parts.append(pet["breed"])
    if pet.get("weight"):
        parts.append(f"{pet['weight']} кг")
    line = "🐾 " + ", ".join(parts)
    if pet.get("allergies"):
        line += f". Алергії: {pet['allergies']}"
    if pet.get("behavior_notes"):
        line += f". Поведінка: {pet['behavior_notes']}"
    return line


def _merge_comment(existing: str, pets_block: str) -> str:
    """Зберегти текст адміністратора, замінити/додати лише блок бота."""
    admin_part = existing.split(BOT_BLOCK_MARKER)[0].rstrip()
    block = f"{BOT_BLOCK_MARKER}\n{pets_block}"
    return f"{admin_part}\n\n{block}" if admin_part else block


def sync_pets_comment(client: dict) -> bool:
    """Записати список улюбленців у коментар клієнта Altegio.

    Повертає True при успіху. Помилки не піднімає — синхронізація не повинна
    ламати флоу бота (адміністратор все одно бачить дані в Supabase).
    """
    company_id = client.get("altegio_company_id")
    altegio_client_id = client.get("altegio_client_id")
    if not company_id or not altegio_client_id:
        return False

    pets = db.get_pets_by_client(client["id"])
    if not pets:
        return False

    pets_block = "\n".join(_pet_line(p) for p in pets)

    try:
        remote = altegio.get_client(company_id, altegio_client_id)
        comment = _merge_comment(remote.get("comment") or "", pets_block)
        altegio.update_client(company_id, altegio_client_id, {
            # ім'я не чіпаємо — передаємо те, що вже стоїть в Altegio
            "name": remote.get("name") or client.get("name") or "",
            "comment": comment,
        })
        return True
    except AltegioError as e:
        logger.warning(f"Не вдалося синхронізувати улюбленців в Altegio (client_id={client['id']}): {e}")
        return False