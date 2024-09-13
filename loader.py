from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from database.model import DB

from config import get_env, load_env, load_config
# from database.models import load
from support import messages

# Загрузка сообщений
messages.load_messages()

# Загрузка файла окружения и файла конфигурации
load_env()
load_config()

# Загрузка базы данных и создание таблиц, если их не существует
DB.load_database()
DB.create_tables()

# Создание бота
bot = Bot(get_env("token"), default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
