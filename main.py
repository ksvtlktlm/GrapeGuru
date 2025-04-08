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
from wine_translations import translate_wine_data


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
    await message.answer("Привет! Я бот, который помогает подобрать вино 🍷\nНапиши название вина, и я попробую найти информацию.")

@dp.message()
async def handle_wine_name(message: types.Message):
    wine_name = message.text.strip()
    await message.answer(f"🔍 Ищу вино: *{escape_markdown(wine_name)}\n*", parse_mode="MarkdownV2")

    wine_data = parse_wine(wine_name=wine_name, headless=True)
    wine_data_translated = translate_wine_data(wine_data)
    wine_text = format_wine_markdown(wine_data_translated)
    if wine_text == "Не удалось найти информацию по данному вину.":
        await message.answer(escape_markdown("❌ Не удалось найти вино!"), parse_mode="MarkdownV2")
        return
    else:
        await message.answer(escape_markdown("🤖 Я проанализировал винную базу и вот, что нашёл для тебя\n:"), parse_mode="MarkdownV2")

        await bot.send_message(
            chat_id=message.chat.id,
            text=wine_text,
            parse_mode="MarkdownV2"
        )


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



