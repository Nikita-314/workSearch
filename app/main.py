import asyncio

import uvicorn

from app.api.app import api_app
from app.bot.bot import bot, dp
from app.bot.handlers import routers
from app.core.config import settings
from app.analytics.storage import init_db


async def start_bot() -> None:
    for router in routers:
        dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    print("Bot started")
    await dp.start_polling(bot)


async def start_api() -> None:
    config = uvicorn.Config(
        app=api_app,
        host="0.0.0.0",
        port=settings.app_port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main() -> None:
    init_db()

    await asyncio.gather(
        start_bot(),
        start_api(),
    )



if __name__ == "__main__":
    asyncio.run(main())