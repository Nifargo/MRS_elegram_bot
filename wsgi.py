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

# Імпортувати Quart додаток
from webhook_bot import app

# Конвертувати ASGI (Quart) в WSGI (PythonAnywhere)
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)
