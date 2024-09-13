from dotenv import load_dotenv
import os

load_dotenv()

# Данные для подключения к БД:
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# Данные для работы с Dadata
DADATA_TOKEN = os.environ.get("DADATA_TOKEN")
DADATA_SECRET = os.environ.get("DADATA_SECRET")
