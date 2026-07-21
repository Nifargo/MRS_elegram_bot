#!/usr/bin/env python3
"""
Скрипт для встановлення webhook URL для Telegram бота.
Запускати ОДИН РАЗ після налаштування Web App на PythonAnywhere.
"""

import sys

import requests
from config import TELEGRAM_TOKEN

# URL твого PythonAnywhere додатку
WEBHOOK_URL = f"https://mrsnoopygrooming.pythonanywhere.com/{TELEGRAM_TOKEN}"

def set_webhook():
    """Встановити webhook URL для бота."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    
    print(f"Встановлюю webhook: {WEBHOOK_URL}")
    
    response = requests.post(url, json=data)
    result = response.json()
    
    if result.get("ok"):
        print("✅ Webhook успішно встановлено!")
        print(f"Опис: {result.get('description')}")
    else:
        print("❌ Помилка встановлення webhook:")
        print(result)

def get_webhook_info() -> str | None:
    """Отримати інформацію про поточний webhook. Повертає поточний url (None при помилці запиту)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"

    response = requests.get(url)
    result = response.json()

    if not result.get("ok"):
        print("❌ Не вдалося отримати інформацію про webhook")
        return None

    info = result.get("result")
    print("\n📋 Інформація про webhook:")
    print(f"URL: {info.get('url')}")
    print(f"Pending updates: {info.get('pending_update_count')}")
    if info.get('last_error_message'):
        print(f"⚠️ Остання помилка: {info.get('last_error_message')}")
        print(f"   Час помилки: {info.get('last_error_date')}")
    return info.get('url')


def check_webhook() -> None:
    """--check: лише перевірити стан (нічого не змінює).

    Локальний `bot.py` (polling) автоматично знімає цей вебхук — після
    локального тесту легко забути його відновити, і продакшн-бот на
    PythonAnywhere замовкає без жодного логу про причину. Цей режим —
    щоб перевірити стан явно, а не покладатись на пам'ять.
    """
    current_url = get_webhook_info()
    if current_url == WEBHOOK_URL:
        print(f"\n✅ Вебхук активний і вказує на PythonAnywhere ({WEBHOOK_URL}).")
    else:
        print("\n🚨 УВАГА: вебхук НЕ вказує на PythonAnywhere!")
        print("   Продакшн-бот зараз НЕ відповідає клієнтам у Telegram.")
        print("   Типова причина: щойно був локальний тест через `python bot.py` (polling).")
        print("   Виправлення: python set_webhook.py")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_webhook()
    else:
        print("🔧 Налаштування webhook для Mr.Snoopy Grooming Bot\n")

        # Встановити webhook
        set_webhook()

        # Перевірити статус
        get_webhook_info()

        print("\n✅ Готово! Тепер бот працює через webhook.")
        print("💡 Можеш закрити всі термінали - бот працюватиме автоматично!")
