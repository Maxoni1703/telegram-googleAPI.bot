import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from sheets_service import SheetsService

# Load environment variables
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Google Sheets Service
try:
    sheets = SheetsService()
except Exception as e:
    logging.error(f"Failed to initialize SheetsService: {e}")
    sheets = None

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для учета расходников.\n\n"
        "Просто напиши название расходника и количество через пробел.\n"
        "Пример: `Масло 5` или `Фильтр 1`"
    )

@dp.message(F.text)
async def handle_consumable(message: Message):
    if not sheets:
        await message.answer("Ошибка: Сервис Google Sheets не настроен. Обратитесь к администратору.")
        return

    # Regular expression to match "Name Quantity" or "Name, Quantity" or "Name - Quantity"
    # Basic logic: split by space and take the last part as quantity
    text = message.text.strip()
    
    # Try to find a number at the end of the message
    match = re.search(r'(.+)\s+(\d+)$', text)
    
    if not match:
        await message.answer(
            "Не удалось распознать формат. Пожалуйста, напиши название и количество через пробел.\n"
            "Пример: `Масло 5`"
        )
        return

    consumable = match.group(1).strip()
    quantity = match.group(2).strip()

    # Get mechanic name from Telegram profile
    user = message.from_user
    mechanic_name = user.full_name
    if not mechanic_name:
        mechanic_name = user.username or f"User_{user.id}"

    try:
        sheets.append_data(mechanic_name, consumable, quantity)
        await message.answer(f"✅ Записано!\n\n🔧 {mechanic_name}\n📦 {consumable}: {quantity}")
    except Exception as e:
        logging.error(f"Error appending data to sheets: {e}")
        await message.answer(f"❌ Ошибка при записи в таблицу: {e}")

async def main():
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
