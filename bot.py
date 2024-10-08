import logging
import sys
import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from data import config
from menucommands.set_bot_commands import set_default_commands
from baza.sqlite import Database
from filters.admin import IsBotAdminFilter
from filters.check_sub_channel import IsCheckSubChannels
from states.reklama import Adverts
from keyboard_buttons import admin_keyboard
from moviepy.editor import VideoFileClip
import os
import aiohttp
import logging
from aiogram.types import CallbackQuery, ContentType
from filters.admin import IsBotAdminFilter,AdminStates

# Konfiguratsiya
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS
MAX_VIDEO_SIZE_MB = 50  # Maksimal video hajmi (MB)
MAX_VIDEO_DURATION = 420  # Maksimal video davomiyligi (soniya)

logging.basicConfig(level=logging.INFO)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(F.content_type == 'video')
async def handle_video(message: types.Message):
    video = message.video
    file_size_mb = video.file_size / (1024 * 1024)  # MB

    if file_size_mb > MAX_VIDEO_SIZE_MB:
        await message.reply("✌☠️✌Video faylning hajmi juda ham  katta. Iltimos, kichikroq yoki short video yuboring.")
        return

    # Ensure the downloads directory exists
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Get the file path
    file = await bot.get_file(video.file_id)
    file_path = file.file_path
    video_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    # Download the video file
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as response:
            if response.status == 200:
                video_path = f"downloads/{video.file_id}.mp4"
                with open(video_path, 'wb') as f:
                    f.write(await response.read())
            else:
                await message.reply("❌🔉🔊 Video faylini yuklab olishda xatolik yuz berdi.")
                return

    # Check video duration and trim if necessary
    video_clip = VideoFileClip(video_path)
    if video_clip.duration > MAX_VIDEO_DURATION:
        # Trim the video to MAX_VIDEO_DURATION
        trimmed_video_path = f"downloads/{video.file_id}_trimmed.mp4"
        trimmed_video_clip = video_clip.subclip(0, MAX_VIDEO_DURATION)
        trimmed_video_clip.write_videofile(trimmed_video_path, codec="libx264")
        video_clip.close()
        video_path = trimmed_video_path
    else:
        video_clip.close()

    # Add delay for processing
    initial_message = await message.reply("📥 Video yuklandi! Konvertatsiya jarayonini kuting...")
    for i in range(3, 0, -1):
        # Send countdown message
        countdown_message = await message.reply(f"⏳ {i} sekunddan so'ng konvertatsiya boshlanadi...")
        
        # Wait 1 second
        await asyncio.sleep(1)
        
        # Delete the previous countdown message
        await countdown_message.delete()
    
    # Delete the initial message
    await initial_message.delete()

    # Convert video to audio using moviepy
    audio_path = f"downloads/{video.file_id}.mp3"
    
    try:
        video_clip = VideoFileClip(video_path)
        video_clip.audio.write_audiofile(audio_path)
        video_clip.close()
    except Exception as e:
        logging.error(f"Error converting video to audio: {e}")
        await message.reply("❌ Audio konvertatsiyasida xatolik yuz berdi. Iltimos, boshqa video yuboring.")
        return

    # Send the audio file back to the user
    audio = FSInputFile(audio_path)
    await message.reply_audio(audio=audio, caption="🔉🔊 Mana, video audiyo formatda!")

    # Clean up files
    try:
        os.remove(video_path)
        os.remove(audio_path)
    except Exception as e:
        logging.error(f"Error cleaning up files: {e}")




@dp.message(CommandStart())
async def start_command(message: Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)  # Add user to the database
        await message.answer(
            text="""<b>Salom! </b> 

<b>Men ¸¸♬·¯·♪·¯·♫¸¸ Vedio to Audio dowlander bot ♫·¯·♪¸♩·¯·♬¸¸  botiman.</b> Sizga quyidagi funksiyalarni taqdim etaman:

<b>/help</b> - Bot qanday ishlashini tushuntiruvchi yordam. 📋
<b>/about</b> - Bot haqidagi ma'lumot va yaratuvchilar haqida. 🛠️

<b>Qanday foydalanish kerak:</b>
Video yuboring va men uni ovozli xabarga aylantiraman. 🎥➡️📋

<b>Agar qo'shimcha savollar yoki yordam kerak bo'lsa:</b>
<b>⚙️ Savollar yoki takliflar uchun</b> <b>⚙️ Savol yoki takliflar</b> tugmasini bosing va admin bilan bog'laning.

<b>Bot Fayozbek Abdimannonovga tomonidan yaratilgan.</b> 🧑‍💻

<b>Botni ishlatganingiz uchun rahmat!</b> 🎉""",
            parse_mode="html"
        )
    except Exception as e:
        await message.answer(
            text="""<b>Salom! 🎉</b> 

<b>Men ¸¸♬·¯·♪·¯·♫¸¸ Vedio to Audio dowlander bot ♫·¯·♪¸♩·¯·♬¸¸  botiman.</b> Sizga quyidagi funksiyalarni taqdim etaman:

<b>/help</b> - Bot qanday ishlashini tushuntiruvchi yordam. 📋
<b>/about</b> - Bot haqidagi ma'lumot va yaratuvchilar haqida. 🛠️

<b>Qanday foydalanish kerak:</b>
Video yuboring va men uni ovozli xabarga aylantiraman. 🎥➡️📋

<b>Agar qo'shimcha savollar yoki yordam kerak bo'lsa:</b>
<b>⚙️ Savollar yoki takliflar uchun</b> <b>⚙️ Savol yoki takliflar</b> tugmasini bosing va admin bilan bog'laning.

<b>Bot  Fayozbek Abdimannonov tomonidan yaratilgan.</b> 🧑‍💻

<b>Botni ishlatganingiz uchun rahmat!</b> """,
            parse_mode="html"
        )

@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message: Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index, channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal", url=ChatInviteLink.invite_link))
    inline_channel.adjust(1, repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga a'zo bo'ling", reply_markup=button)

@dp.message(Command("help"))
async def help_commands(message: Message):
    await message.answer("""<b>👋 Salom!</b> Men ¸¸♬·¯·♪·¯·♫¸¸ Vedio to Audio dowlander bot ♫·¯·♪¸♩·¯·♬¸¸ botiman. Sizga quyidagi funksiyalarni taqdim etaman:

<b>1. /start</b> - Botni ishga tushiradi va siz bilan salomlashadi.🤖 
<b>2. /help</b> - Botning qanday ishlashini tushuntiruvchi yordam. 📋
<b>3. /about</b> - Bot yaratuvchilari va bot haqidagi to'liq ma'lumotlar. 🛠️

<b>📌 Qanday foydalanish kerak:</b>
- Video yuboring va men uni ovozli faylga aylantiraman. 🎥➡️📋

<b>Agar qo'shimcha yordam kerak bo'lsa:</b>
- <b>⚙️ Savollar yoki takliflar uchun</b> savol yoki takliflar tugmasini bosing va admin bilan bog'laning.

<b>Bot Fayozbek Abdimannonovga tomonidan yaratilgan. 🧑‍💻 </b>

<b>Rahmat, Men ¸¸♬·¯·♪·¯·♫¸¸ Vedio to Audio dowlander bot ♫·¯·♪¸♩·¯·♬¸¸!</b>""", parse_mode="html")

@dp.message(Command("about"))
async def about_commands(message: Message):
    await message.answer("""<b>📢 /about - Bot Haqida Ma'lumot</b>

<b>👋 Salom! Men ¸¸♬·¯·♪·¯·♫¸¸ Vedio to Audio dowlander bot ♫·¯·♪¸♩·¯·♬¸¸ botiman.</b>

<b>Bot Yaratuvchilari:</b>
- <b>Yaratuvchi:</b> Fayozbek Abdimannonov
- <b>Tajriba:</b> Backend dasturchi, Django bo'yicha mutaxassis
- <b>Maqsad:</b> Ushbu bot sizga matnni ovozga aylantirish va boshqa imkoniyatlarni taqdim etish uchun yaratilgan.

<b>Bot Haqida:</b>
- <b>Maqsad:</b>  ¸¸♬·¯·♪·¯·♫¸¸ Vedio to Audio dowlander bot ♫·¯·♪¸♩·¯·♬¸¸ bot sizning matnlaringizni ovozli xabarlarga aylantiradi. Har qanday matnni yuboring va men uni sizga ovozli xabar sifatida qaytaraman.
- <b>Texnologiyalar:</b> Bot Python dasturlash tili yordamida yaratildi va <b>aiogram</b> kutubxonasi, <b>gTTS</b> (Google Text-to-Speech) kabi texnologiyalarni ishlatadi.
- <b>Qanday Ishlaydi:</b> Siz matn yuborganingizda, bot uni ovozga aylantiradi va ovozli xabar sifatida yuboradi.

<b>Agar Qo'shimcha Ma'lumot yoki Yordam Kerak Bo'lsa:</b>
- <b>Elektron pochta:</b> <b>fayozbek898@gmail.com 📧</b>
- <b>Telegram:</b> <b>https://t.me/PREMIUM_777_BEK 🧑‍💻</b>

<b>Rahmat va botni ishlatganingiz uchun rahmat!</b> 📨""", parse_mode='html')
    

@dp.message(lambda message: message.text == '📨 Savollar va takliflar')
async def handle_savol_takliflar(message: Message, state: FSMContext):
    # Foydalanuvchiga admin uchun xabar yuborish uchun taklif qiluvchi matn
    await message.answer(
        "<b>📩+🧑‍💻 Sizning fikr va savollaringiz biz uchun muhim!</b>\n\n"
        "Iltimos, admin uchun xabar yuboring. Sizning savolingiz yoki taklifingiz "
        "tez orada ko'rib chiqiladi va sizga javob beriladi.\n\n"
        "<i>Matn, rasm, audio yoki boshqa turdagi fayllarni yuborishingiz mumkin.</i>",
        parse_mode='html'
    )
    await state.set_state(AdminStates.waiting_for_admin_message)

# Handle messages sent by the user for the admin
@dp.message(AdminStates.waiting_for_admin_message, F.content_type.in_([
    ContentType.TEXT, ContentType.AUDIO, ContentType.VOICE, ContentType.VIDEO,
    ContentType.PHOTO, ContentType.ANIMATION, ContentType.STICKER, 
    ContentType.LOCATION, ContentType.DOCUMENT, ContentType.CONTACT,
    ContentType.VIDEO_NOTE
]))
async def handle_admin_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    # Foydalanuvchi ma'lumotlarini identifikatsiya qilish
    if username:
        user_identifier = f"@{username}"
    else:
        user_identifier = f"{first_name} {last_name}".strip()

    # Har bir admin uchun foydalanuvchi xabarini yuborish
    for admin_id in config.ADMINS:
        try:
            if message.video_note:
                await bot.send_video_note(
                    admin_id,
                    message.video_note.file_id,
                )
            elif message.text:
                await bot.send_message(
                    admin_id,
                    f"<b>Foydalanuvchi:</b> {user_identifier}\n\n"
                    f"<b>Xabar:</b>\n{message.text}",
                    parse_mode='html'
                )
            elif message.audio:
                await bot.send_audio(
                    admin_id,
                    message.audio.file_id,
                    caption=f"<b>Foydalanuvchi:</b> {user_identifier}\n\n<b>Audio xabar</b>",
                    parse_mode='html'
                )
            elif message.voice:
                await bot.send_voice(
                    admin_id,
                    message.voice.file_id,
                    caption=f"<b>Foydalanuvchi:</b> {user_identifier}\n\n<b>Ovozli xabar</b>",
                    parse_mode='html'
                )
            elif message.video:
                await bot.send_video(
                    admin_id,
                    message.video.file_id,
                    caption=f"<b>Foydalanuvchi:</b> {user_identifier}\n\n<b>Video xabar</b>",
                    parse_mode='html'
                )
            elif message.photo:
                await bot.send_photo(
                    admin_id,
                    message.photo[-1].file_id,
                    caption=f"<b>Foydalanuvchi:</b> {user_identifier}\n\n<b>Rasm xabar</b>",
                    parse_mode='html'
                )
            elif message.animation:
                await bot.send_animation(
                    admin_id,
                    message.animation.file_id,
                    caption=f"<b>Foydalanuvchi:</b> {user_identifier}\n\n<b>GIF xabar</b>",
                    parse_mode='html'
                )
            elif message.sticker:
                await bot.send_sticker(
                    admin_id,
                    message.sticker.file_id,
                )
            elif message.location:
                await bot.send_location(
                    admin_id,
                    latitude=message.location.latitude,
                    longitude=message.location.longitude,
                )
            elif message.document:
                await bot.send_document(
                    admin_id,
                    message.document.file_id,
                    caption=f"<b>Foydalanuvchi:</b> {user_identifier}\n\n<b>Hujjat xabar</b>",
                    parse_mode='html'
                )
            elif message.contact:
                await bot.send_contact(
                    admin_id,
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=message.contact.last_name or "",
                )
        except Exception as e:
            logging.error(f"Error sending message to admin {admin_id}: {e}")

    # Foydalanuvchiga xabar yuborish
    await state.clear()
    await bot.send_message(
        user_id,
        "<b> 🧑‍💻Xabaringiz muvaffaqiyatli yuborildi!</b>\n\n"
        "Admin tez orada siz bilan bog'lanadi. Sizning savolingiz yoki taklifingiz "
        "biz uchun juda muhim. Iltimos, sabr qiling va javobni kuting.",
        parse_mode='html'
    )


@dp.message(Command("admin"), IsBotAdminFilter(ADMINS))
async def is_admin(message: Message):
    await message.answer(text="Admin menu", reply_markup=admin_keyboard.admin_button)

@dp.message(F.text == "Foydalanuvchilar soni", IsBotAdminFilter(ADMINS))
async def users_count(message: Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "Reklama yuborish", IsBotAdminFilter(ADMINS))
async def advert_dp(message: Message, state: FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin!", parse_mode=ParseMode.HTML)

@dp.message(Adverts.adverts)
async def send_advert(message: Message, state: FSMContext):
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0], from_chat_id=from_chat_id, message_id=message_id)
            count += 1
        except Exception as e:
            logging.exception(f"Foydalanuvchiga reklama yuborishda xatolik: {user[0]}", e)
        time.sleep(0.01)
    
    await message.answer(f"Reklama {count} ta foydalanuvchiga yuborildi", parse_mode=ParseMode.HTML)
    await state.clear()

@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=int(admin),
                text="<b>🔔 Bot muvaffaqiyatli ishga tushdi!</b>\n\n"
                     "Bot endi to'liq faol va foydalanuvchilar bilan muloqotga tayyor. "
                     "Agar biror bir muammo yuzaga kelsa, tezda xabar bering.",
                parse_mode='html'
            )
        except Exception as err:
            logging.exception(f"Admin {admin} uchun xabar yuborishda xatolik yuz berdi: {err}")

# Bot ishdan to'xtaganda barcha adminlarni xabardor qilish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=int(admin),
                text="<b>❌ Bot ishdan to'xtadi!</b>\n\n"
                     "Bot faoliyati to'xtatildi. Agar bu rejalashtirilmagan bo'lsa, "
                     "iltimos, darhol tekshiring va botni qayta ishga tushiring.",
                parse_mode='html'
            )
        except Exception as err:
            logging.exception(f"Admin {admin} uchun xabar yuborishda xatolik yuz berdi: {err}")

from help_stt import Help


# Xabar yuborish komandasi
@dp.message(Command("xabar"))
async def help_commands(message: Message, state: FSMContext):
    await message.answer("Xabaringizni yozib ✍🏻 \nMurojatingiz 👤 adminga boradi !")
    await state.set_state(Help.help)
    

# Foydalanuvchining adminga yozgan xabarini jo'natish
@dp.message(Help.help)
async def send_advert(message: Message, state: FSMContext):
    try:
        # await bot.send_message(ADMINS[0],"📌 Yangi xabar")
        msg = f"{message.from_user.id} 📌 \n\nYangi xabar\n\n"
        msg += f"{message.text}"
        await bot.send_message(ADMINS[0], msg,parse_mode="html")
        await message.answer("Xabaringiz adminga yetkazildi")
        await state.clear()
        
    except:
        
        await message.answer("Faqat matn ko'rinishidagi xabarlarni yubora olasiz.")
        await message.answer("Marhamat adminga xabaringizni qoldiring.")


@dp.message(F.reply_to_message, IsBotAdminFilter(ADMINS))
async def is_admin(message: Message):
    try:    
            u_id = message.reply_to_message.text.split()[0]
            print(u_id, "*************")
            text = message.text
            await bot.send_message(int(u_id), text)
            await message.answer("xabaringiz yetkazildi. ")
    except:
        await message.answer("Nimadir xato bo'ldi")

def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    from middlewares.throttling import ThrottlingMiddleware
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))

async def main() -> None:
    global bot, db
    bot = Bot(TOKEN)
    db = Database(path_to_db="main.db")
    await set_default_commands(bot)
    setup_middlewares(dispatcher=dp, bot=bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())