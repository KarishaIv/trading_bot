import asyncio
import logging
from aiogram import Bot, Dispatcher

from handlers import user_start, user_actions, news_callbacks
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_routers(
    user_start.router,
    user_actions.router,
    news_callbacks.router
)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
