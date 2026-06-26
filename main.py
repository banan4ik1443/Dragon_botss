"""
Точка входа бота. Запуск: python main.py (нужен BOT_TOKEN в .env или окружении).
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import start, profile, dragon, eggs, shop, pvp, explore, quests, top


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(dragon.router)
    dp.include_router(eggs.router)
    dp.include_router(shop.router)
    dp.include_router(pvp.router)
    dp.include_router(explore.router)
    dp.include_router(quests.router)
    dp.include_router(top.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
