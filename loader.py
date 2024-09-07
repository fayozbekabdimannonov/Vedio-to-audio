from aiogram import Bot, Dispatcher
from data import config
from baza.sqlite import Database

# Adminlar va tokenlar sozlamalarini olish
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

# Bot obyektini yaratish
bot = Bot(token=TOKEN,parse_mode="html")

# Ma'lumotlar bazasi obyektini yaratish
db = Database(path_to_db="main.db")

# Dispatcher yaratish (v3 versiyasida bot obyektini olishini tekshiring)
dp = Dispatcher(bot=bot)

