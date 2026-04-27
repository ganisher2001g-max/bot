import sqlite3
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "8676192292:AAFOlS6nPfxQSFQ7Q7mPXz_Y44JMzQu8kaI"
ADMIN_ID = 8443902786

bot = Bot(token=TOKEN)
dp = Dispatcher()

class FeedbackState(StatesGroup):
    waiting = State()

class BroadcastState(StatesGroup):
    waiting = State()
    confirm = State()

class SearchState(StatesGroup):
    waiting = State()

def init_db():
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS lessons")
    cursor.execute('''CREATE TABLE lessons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT,
                        title TEXT,
                        url TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedbacks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username TEXT,
                        full_name TEXT,
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        full_name TEXT,
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    darslar = [
        ('domofon', 'Hikvision Gibrid domofon sozlash', 'https://youtu.be/d3hScVm4gRA'),
        ('domofon', 'Dahua domofon sozlash', 'https://youtu.be/5r2eMTB3dro'),
        ('domofon', 'Hikvision IP domofon sozlash (1-qism)', 'https://youtu.be/FAlNuxE2R0E'),
        ('domofon', 'Hikvision IP domofon sozlash (2-qism)', 'https://youtu.be/vzQMhTy0L48'),
        ('wifi', 'Ezviz kameralar (Playlist)', 'https://youtube.com/playlist?list=PL_JB_UjrBokcKCOexjG2wrv2ypBsmqoUj'),
        ('wifi', 'Xitoy no name Smart 360 kamera', 'https://youtu.be/CZlIAsPsFEw'),
        ('ip', 'Hikvision IP kameralarni sozlash (1-qism)', 'https://youtu.be/moRbjD4yShM'),
        ('ip', 'Hikvision IP kameralarni sozlash (2-qism)', 'https://youtu.be/wt2JmymLpgM'),
        ('ip', 'Hikvision IP kameralarni sozlash (3-qism)', 'https://youtu.be/R6gaJ0sp_9g'),
        ('ip', 'Hikvision IP kameralarni sozlash (4-qism)', 'https://youtu.be/WL0aBcbGIus'),
        ('ip', 'Hikvision IP kameralarni sozlash (5-qism)', 'https://youtu.be/QTs-prSQweY'),
        ('ip', 'Hikvision kameralarni Hik-Connect ga togri ulash (1-qism)', 'https://youtu.be/OZmmahviNU0'),
        ('ip', 'Hikvision kameralarni Hik-Connect ga togri ulash (2-qism)', 'https://youtu.be/VPuxCiyvzWA'),
        ('ip', 'Dahua IP kamerasini sozlash', 'https://youtu.be/X_ToOFfCwTg'),
        ('ip', 'Hik-Connectda akkaunt qoshish va ikkinchi telefon qoshish', 'https://youtube.com/playlist?list=PL_JB_UjrBokeC7JukpXbFDONPtkSA9kvj'),
        ('zavod', 'NVR ni sbros qilish', 'https://youtu.be/YmVzhnv_FQA'),
        ('zavod', 'Hik-Connect orqali sbros qilish', 'https://youtu.be/R4eJec6EJe0'),
        ('zavod', 'Grafik kalit orqali sbros qilish', 'https://youtu.be/yQcS_f_bZJw'),
        ('zavod', 'Hik-Partner orqali sbros qilish', 'https://youtu.be/noBeasSgXPA'),
        ('zavod', 'Hik-Partner Pro orqali sbros qilish', 'https://youtu.be/gAg-W0lZ6SM'),
        ('zavod', 'Domofonni sbros qilish', 'https://youtu.be/HSyL_a2mcjM'),
        ('zavod', 'Tiandy kameralarini sbros qilish (Playlist)', 'https://youtube.com/playlist?list=PL_JB_UjrBokduAydDkjdzWsPR6oozvmd4'),
        ('montaj', 'Montaj asoslari', 'https://youtu.be/F_4nJZBHLcM'),
        ('montaj', 'IP kamera montaji', 'https://youtu.be/xEibgZVVrXU'),
        ('montaj', 'RJ 45 tayyorlash', 'https://youtube.com/shorts/FYW23lS297U')
    ]
    cursor.executemany("INSERT INTO lessons (category, title, url) VALUES (?, ?, ?)", darslar)
    conn.commit()
    conn.close()

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Darsliklar")
    kb.button(text="Test topshirish")
    kb.button(text="Fikr qoldirish")
    kb.button(text="Qidiruv")
    kb.button(text="Aloqa")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def categories_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Domofonlar", callback_data="cat_domofon")
    kb.button(text="Wi-Fi kameralar", callback_data="cat_wifi")
    kb.button(text="IP kameralar", callback_data="cat_ip")
    kb.button(text="Montaj darslari", callback_data="cat_montaj")
    kb.button(text="Zavod holatiga qaytarish", callback_data="cat_zavod")
    kb.adjust(2)
    return kb.as_markup()

def back_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="Orqaga", callback_data="back_to_cats")
    return kb.as_markup()

def save_user(user: types.User):
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (user.id, user.username or "yoq", user.full_name))
    conn.commit()
    conn.close()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    save_user(message.from_user)
    await message.answer("Assalomu alaykum, " + message.from_user.full_name + "!\nAbu Security akademiyasi botiga xush kelibsiz.", reply_markup=main_menu())

@dp.message(Command("users"))
async def show_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz.")
        return
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT user_id, username, full_name, joined_at FROM users ORDER BY joined_at DESC LIMIT 20")
    users = cursor.fetchall()
    conn.close()
    text = "A'zolar soni: " + str(total) + "\n\nSo'ngi 20 ta:\n\n"
    for uid, uname, fname, date in users:
        text += "ID: " + str(uid) + "\nIsm: " + fname + "\n@" + uname + "\nQo'shildi: " + str(date) + "\n\n"
    await message.answer(text)

@dp.message(Command("stat"))
async def show_stat(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz.")
        return
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM users WHERE date(joined_at) = ?", (today,))
    today_count = cursor.fetchone()[0]
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM users WHERE date(joined_at) >= ?", (week_ago,))
    week_count = cursor.fetchone()[0]
    conn.close()
    await message.answer("Statistika:\n\nJami a'zolar: " + str(total) + "\nBugun qo'shilgan: " + str(today_count) + "\nSo'nggi 7 kun: " + str(week_count))

@dp.message(Command("send"))
async def cmd_send(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Barchaga yuboriladigan xabarni yozing.\nBekor qilish uchun /start bosing.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(BroadcastState.waiting)

@dp.message(BroadcastState.waiting)
async def process_broadcast_text(message: types.Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    kb = InlineKeyboardBuilder()
    kb.button(text="Ha, yuborish", callback_data="confirm_broadcast")
    kb.button(text="Bekor qilish", callback_data="cancel_broadcast")
    await message.answer("Xabar:\n\n" + message.text + "\n\nYuborilsinmi?", reply_markup=kb.as_markup())
    await state.set_state(BroadcastState.confirm)

@dp.callback_query(F.data == "confirm_broadcast", BroadcastState.confirm)
async def confirm_broadcast(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("broadcast_text")
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    sent = 0
    failed = 0
    for (user_id,) in users:
        try:
            await bot.send_message(user_id, text)
            sent += 1
        except Exception:
            failed += 1
    await callback.message.edit_text("Yuborildi: " + str(sent) + "\nMuvaffaqiyatsiz: " + str(failed))
    await callback.answer()
    await state.clear()

@dp.callback_query(F.data == "cancel_broadcast", BroadcastState.confirm)
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Bekor qilindi.")
    await callback.answer()
    await state.clear()

@dp.message(F.text == "Darsliklar")
async def show_categories(message: types.Message):
    await message.answer("Yonalishni tanlang:", reply_markup=categories_menu())

@dp.callback_query(F.data == "back_to_cats")
async def go_back(callback: types.CallbackQuery):
    await callback.message.edit_text("Yonalishni tanlang:", reply_markup=categories_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def show_lessons(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, url FROM lessons WHERE category=?", (category,))
    lessons = cursor.fetchall()
    conn.close()
    if not lessons:
        await callback.message.edit_text("Hozircha darslar mavjud emas.", reply_markup=back_button())
    else:
        text = "Bolim darslari:\n\n"
        for title, url in lessons:
            text += title + "\n" + url + "\n\n"
        await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.message(F.text == "Test topshirish")
async def start_test(message: types.Message):
    await message.answer("Tez orada bu bolimda bilimingizni tekshirish uchun testlar paydo boladi!")

@dp.message(F.text == "Aloqa")
async def contact_admin(message: types.Message):
    await message.answer("Aloqa ma'lumotlari:\n\nFirma: Abu Security Solutions\nMas'ul: Muhammadaminov Abdulloh\nTelefon: +998200154141\nTelegram kanal: @ass_uz\nShaxsiy lichka: @ASS_adm1n")

@dp.message(F.text == "Fikr qoldirish")
async def ask_feedback(message: types.Message, state: FSMContext):
    await message.answer("Fikringizni yozing. Adminlar uni ko'rib chiqadi.\n\nBekor qilish uchun /start bosing.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(FeedbackState.waiting)

@dp.message(FeedbackState.waiting)
async def process_feedback(message: types.Message, state: FSMContext):
    user = message.from_user
    username = user.username if user.username else "yoq"
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedbacks (user_id, username, full_name, message) VALUES (?, ?, ?, ?)", (user.id, username, user.full_name, message.text))
    conn.commit()
    conn.close()
    await bot.send_message(ADMIN_ID, "Yangi fikr!\n\nKimdan: " + user.full_name + " (@" + username + ")\nID: " + str(user.id) + "\n\nXabar:\n" + message.text)
    await message.answer("Rahmat! Fikringiz qabul qilindi.", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "Qidiruv")
async def ask_search(message: types.Message, state: FSMContext):
    await message.answer("Qidirish uchun kalit so'z yozing.\nMasalan: Hikvision, Dahua, montaj, sbros...", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SearchState.waiting)

@dp.message(SearchState.waiting)
async def process_search(message: types.Message, state: FSMContext):
    keyword = message.text.lower()
    conn = sqlite3.connect('academy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, url FROM lessons WHERE LOWER(title) LIKE ?", ("%" + keyword + "%",))
    results = cursor.fetchall()
    conn.close()
    if not results:
        await message.answer("'" + message.text + "' bo'yicha hech narsa topilmadi.", reply_markup=main_menu())
    else:
        text = "'" + message.text + "' bo'yicha natijalar:\n\n"
        for title, url in results:
            text += title + "\n" + url + "\n\n"
        await message.answer(text, reply_markup=main_menu())
    await state.clear()

async def main():
    init_db()
    print("BOT TAYYOR VA ISHGA TUSHDI!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())