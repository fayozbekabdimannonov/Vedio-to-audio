from aiogram import Bot
from aiogram.methods.set_my_commands import BotCommand
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.types import Message
from loader import dp, bot, ADMINS, db
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State  # Holatlarni import qilish

# Help klassini to'g'ri yaratish
class Help(StatesGroup):
    help = State()

# Default komandalarni o'rnatish
async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Botni ishga tushirish"),
        BotCommand(command="/help", description="yordam so`rash"),
        BotCommand(command="/about", description="Botning admini !"),
        BotCommand(command="/xabar", description="Adminga xabar yuborish"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
