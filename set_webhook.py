#!/usr/bin/env python3
"""
Скрипт для встановлення webhook URL для Telegram бота.
Запускати ОДИН РАЗ після налаштування Web App на PythonAnywhere.
"""

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

def get_webhook_info():
    """Отримати інформацію про поточний webhook."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    
    response = requests.get(url)
    result = response.json()
    
    if result.get("ok"):
        info = result.get("result")
        print("\n📋 Інформація про webhook:")
        print(f"URL: {info.get('url')}")
        print(f"Pending updates: {info.get('pending_update_count')}")
        if info.get('last_error_message'):
            print(f"⚠️ Остання помилка: {info.get('last_error_message')}")
            print(f"   Час помилки: {info.get('last_error_date')}")
    else:
        print("❌ Не вдалося отримати інформацію про webhook")

if __name__ == "__main__":
    print("🔧 Налаштування webhook для Mr.Snoopy Grooming Bot\n")
    
    # Встановити webhook
    set_webhook()
    
    # Перевірити статус
    get_webhook_info()
    
    print("\n✅ Готово! Тепер бот працює через webhook.")
    print("💡 Можеш закрити всі термінали - бот працюватиме автоматично!")
