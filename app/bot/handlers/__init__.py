from app.bot.handlers.search import router as search_router
from app.bot.handlers.start import router as start_router

routers = [
    start_router,
    search_router,
]