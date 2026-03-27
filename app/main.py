import asyncio

import uvicorn

from app.api.app import api_app
from app.bot.bot import bot, dp
from app.bot.handlers import routers


async def start_bot() -> None:
    for router in routers:
        dp.include_router(router)

    print("Bot started")
    await dp.start_polling(bot)


async def start_api() -> None:
    config = uvicorn.Config(
        app=api_app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    await asyncio.gather(
        start_bot(),
        start_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())