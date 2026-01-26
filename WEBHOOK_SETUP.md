# 🚀 Налаштування Webhook для Mr.Snoopy Grooming Bot

## Чому webhook краще за polling?

**Polling (старий спосіб):**
- Бот постійно питає Telegram "є нові повідомлення?"
- ❌ PythonAnywhere free tier блокує такі запити (503 error)
- Більше навантаження на сервер

**Webhook (новий спосіб):**
- Telegram САМ надсилає повідомлення на твій сервер
- ✅ Працює на PythonAnywhere free tier
- Швидше і ефективніше

---

## 📋 Інструкція з налаштування

### 1. Завантажити зміни на GitHub (на Mac)

```bash
cd ~/path/to/MRS_elegram_bot
git add .
git commit -m "Switch to webhook mode"
git push origin main
```

### 2. Оновити код на PythonAnywhere

Зайди в **Bash Console** на PythonAnywhere:

```bash
cd ~/MRS_elegram_bot
git pull origin main
. venv/bin/activate
pip install -r requirements.txt
```

### 3. Зупинити старий polling бот (якщо працює)

```bash
pkill -f bot.py
```

### 4. Налаштувати Web App на PythonAnywhere

1. Йди на вкладку **Web** в PythonAnywhere Dashboard
2. Натисни **Add a new web app**
3. Обери домен: `mrsnoopygrooming.pythonanywhere.com`
4. Обери **Manual configuration** (не Flask wizard!)
5. Обери **Python 3.10**

### 5. Налаштувати WSGI файл

На вкладці **Web**, знайди розділ **Code**:

**WSGI configuration file:** натисни на посилання (щось на зразок `/var/www/mrsnoopygrooming_pythonanywhere_com_wsgi.py`)

**ВИДАЛИ ВСЕ** з цього файлу і вставте:

```python
import sys
import os

# Додати шлях до проекту
path = '/home/MrSnoopyGrooming/MRS_elegram_bot'
if path not in sys.path:
    sys.path.insert(0, path)

# Завантажити .env
from dotenv import load_dotenv
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Імпортувати Flask додаток
from webhook_bot import app as application
```

Збережи файл (Ctrl+S або кнопка Save).

### 6. Налаштувати Virtualenv

На вкладці **Web**, знайди розділ **Virtualenv**:

**Enter path to a virtualenv:**
```
/home/MrSnoopyGrooming/MRS_elegram_bot/venv
```

### 7. Перезавантажити Web App

Натисни велику зелену кнопку **Reload mrsnoopygrooming.pythonanywhere.com**

### 8. Перевірити що сайт працює

Відкрий в браузері:
```
https://mrsnoopygrooming.pythonanywhere.com/
```

Має показати: `🐾 Mr.Snoopy Grooming Bot is running!`

### 9. Встановити webhook URL

В **Bash Console** на PythonAnywhere:

```bash
cd ~/MRS_elegram_bot
. venv/bin/activate
python set_webhook.py
```

Має показати:
```
✅ Webhook успішно встановлено!
```

---

## ✅ Готово!

Тепер бот працює через webhook! 

**Можеш:**
- ✅ Закрити всі консолі PythonAnywhere
- ✅ Закрити браузер
- ✅ Вимкнути комп'ютер

**Бот працює автоматично 24/7!**

---

## 🔍 Як перевірити що працює?

### 1. Напиши боту в Telegram

Якщо відповідає - все ОК! ✅

### 2. Перевір webhook статус

```bash
cd ~/MRS_elegram_bot
. venv/bin/activate
python set_webhook.py
```

### 3. Подивись логи Flask

На вкладці **Web** → **Log files** → **Error log**

---

## 🛠️ Troubleshooting

### Бот не відповідає?

1. Перевір що Web App запущений (зелена галочка на вкладці Web)
2. Перевір error log
3. Перезавантаж Web App (кнопка Reload)

### Webhook помилка?

```bash
python set_webhook.py
```

Подивись що пише в "Остання помилка"

### Код оновився, але бот працює зі старою версією?

Натисни **Reload** на вкладці Web в PythonAnywhere

---

## 🔄 Як оновлювати бота в майбутньому?

### На Mac:
```bash
git add .
git commit -m "опис змін"
git push origin main
```

### На PythonAnywhere:
```bash
cd ~/MRS_elegram_bot
git pull origin main
. venv/bin/activate
pip install -r requirements.txt  # якщо змінювались залежності
```

Потім на вкладці **Web** натисни **Reload** ⟳

---

## 📊 Переваги webhook над polling

✅ Працює на PythonAnywhere free tier  
✅ Швидша відповідь (без затримки)  
✅ Менше навантаження на сервер  
✅ Не потрібно тримати запущений процес (Flask працює автоматично)  
✅ Автоматичний перезапуск після помилок  

---

## ⚠️ Важливо!

- Webhook працює ТІЛЬКИ з HTTPS (PythonAnywhere дає безкоштовно)
- Старий `bot.py` (polling) більше НЕ ВИКОРИСТОВУЄТЬСЯ
- Не запускай `bot.py` і webhook одночасно - буде конфлікт!
- Не потрібно нічого запускати через `nohup` - Flask працює автоматично!

---

🐾 **Успіхів з ботом Mr.Snoopy Grooming!**
