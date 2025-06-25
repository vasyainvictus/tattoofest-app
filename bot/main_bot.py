# bot/main_bot.py

import asyncio
import logging
import os
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo 
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ЗАГЛУШКИ: Сюда мы вставим публичные URL от VS Code
WEB_APP_URL = "https://tattoofest-app.vercel.app" 
BACKEND_URL = "https://tattoofest-app.vercel.app/api"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Registration(StatesGroup):
    waiting_for_access_code = State()

def check_user_in_backend(telegram_id: int):
    try:
        response = requests.get(f"{BACKEND_URL}/users/by_telegram_id/{telegram_id}")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при проверке пользователя: {e}")
        return None

def activate_user_in_backend(telegram_id: int, access_code: str):
    try:
        response = requests.post(f"{BACKEND_URL}/activate_user", json={"telegram_id": telegram_id, "access_code": access_code})
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при активации пользователя: {e}")
        return None

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    user_data = check_user_in_backend(message.from_user.id)
    if user_data:
        role = user_data.get('role', 'неизвестна').capitalize()
        web_app_info = WebAppInfo(url=WEB_APP_URL)
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Открыть личный кабинет", web_app=web_app_info)]], resize_keyboard=True)
        await message.answer(f"Снова здравствуйте, {message.from_user.full_name}!\nВаша роль: **{role}**.", reply_markup=keyboard)
    else:
        await message.answer(f"Привет, {message.from_user.full_name}!\nВведите ваш код доступа.")
        await state.set_state(Registration.waiting_for_access_code)

@dp.message(Registration.waiting_for_access_code, F.text)
async def process_access_code(message: types.Message, state: FSMContext):
    user_data = activate_user_in_backend(message.from_user.id, message.text.strip())
    if user_data:
        role = user_data.get('role', 'неизвестна').capitalize()
        web_app_info = WebAppInfo(url=WEB_APP_URL)
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Открыть личный кабинет", web_app=web_app_info)]], resize_keyboard=True)
        await message.answer(f"Отлично! Код принят.\nВы зарегистрированы с ролью: **{role}**.", reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("Увы, этот код недействителен или уже был использован.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
