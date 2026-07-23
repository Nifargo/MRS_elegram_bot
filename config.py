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

# Локації салону: назва -> посилання "Залишити відгук" на Google Maps (Фаза 4, оцінка 5⭐+5⭐)
GOOGLE_MAPS_REVIEW_URLS = {
    "Замарстинівська": "https://search.google.com/local/writereview?placeid=ChIJDRoc94_dOkcRrXWt_k2e2xQ",
    "Тернопільська": "https://search.google.com/local/writereview?placeid=ChIJSeDLivznOkcR60tDmWm7GIs",
    "Володимира Великого": "https://search.google.com/local/writereview?placeid=ChIJWws03CfnOkcRMdCOMgg1VkE",
}

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Внутрішній секрет для /cron ендпоінта (викликається зовнішнім планувальником)
CRON_SECRET = os.getenv("CRON_SECRET")

# Внутрішній секрет для /altegio/webhook ендпоінта (URL реєструється в Altegio)
ALTEGIO_WEBHOOK_SECRET = os.getenv("ALTEGIO_WEBHOOK_SECRET")

# Група адмінів: усі сповіщення (новий користувач, незаповнена анкета тощо)
# летять одним повідомленням у конкретний топік супергрупи.
ADMIN_GROUP_CHAT_ID = int(os.getenv("ADMIN_GROUP_CHAT_ID")) if os.getenv("ADMIN_GROUP_CHAT_ID") else None
ADMIN_TOPIC_ID = int(os.getenv("ADMIN_TOPIC_ID")) if os.getenv("ADMIN_TOPIC_ID") else None

# Номер салону для кнопки "🆘 Допомога" (Фаза 9)
HELP_PHONE = "+380960080482"

# Пряме посилання на онлайн-запис Altegio — єдиний віджет на всі 3 філії,
# клієнт сам обирає локацію/послугу/дату/час всередині нього.
ALTEGIO_BOOKING_WIDGET_URL = "https://n1358931.alteg.io/"

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