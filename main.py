import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests
from io import BytesIO
from message_formatter import escape_markdown, format_wine_markdown
from parser_vivino import parse_wine


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Это бот вина!")

    # Отправляем тестовое вино
    wine_data = parse_wine('Cabernet', headless=False)
    wine_text = format_wine_markdown(wine_data)
    if wine_text == "Не удалось найти информацию по данному вину.":
        await message.answer(escape_markdown("❌ Не удалось найти вино!"), parse_mode="MarkdownV2")
        return

    await bot.send_message(
        chat_id=message.chat.id,
        text=wine_text,
        parse_mode="MarkdownV2"
    )


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



