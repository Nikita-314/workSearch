import asyncio

from app.bot.bot import bot, dp
from app.bot.handlers import routers


async def main():
    # подключаем роутеры
    for router in routers:
        dp.include_router(router)

    print("Bot started 🚀")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())