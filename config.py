import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Altegio API
ALTEGIO_PARTNER_TOKEN = os.getenv("ALTEGIO_PARTNER_TOKEN")
ALTEGIO_USER_TOKEN = os.getenv("ALTEGIO_USER_TOKEN")

# Локації салону: назва -> company_id в Altegio
ALTEGIO_LOCATIONS = {
    "Замарстинівська": os.getenv("ALTEGIO_COMPANY_IDS_Zam"),
    "Тернопільська": os.getenv("ALTEGIO_COMPANY_IDS_Tern"),
    "Володимира Великого": os.getenv("ALTEGIO_COMPANY_IDS_Vel"),
}

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Внутрішній секрет для /cron ендпоінта (викликається зовнішнім планувальником)
CRON_SECRET = os.getenv("CRON_SECRET")

# Telegram chat_id адміністраторів, яким летять сповіщення
ADMIN_CHAT_IDS = [
    int(chat_id) for chat_id in os.getenv("ADMIN_CHAT_IDS", "").split(",") if chat_id.strip()
]

SYSTEM_PROMPT = """
Ти - досвідчений консультант грумінг-салону "Mr.Snoopy Grooming".
Ти допомагаєш клієнтам з питаннями:
- Послуги грумінгу (стрижка, купання, тримінг, чистка вух/зубів)
- Запис на прийом
- Догляд за шерстю вдома
- Рекомендації по частоті грумінгу для різних порід

Щодо цін - ввічливо направляй клієнтів зв'язатися з адміністратором для уточнення.
Відповідай дружньо, як справжній консультант. Будь корисним та терплячим.
Спілкуйся українською мовою.
Відповідай коротко та по суті, без зайвих вступів.
"""

WELCOME_MESSAGE = """
Вітаю! 🐾

Я консультант грумінг-салону Mr.Snoopy Grooming.
Із задоволенням допоможу вам з питаннями про догляд за вашим улюбленцем!

Запитуйте про:
• Послуги грумінгу
• Запис на прийом
• Догляд за шерстю вдома
• Рекомендації для вашої породи
"""