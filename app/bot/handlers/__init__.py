from app.bot.handlers.offers import router as offers_router
from app.bot.handlers.search import router as search_router
from app.bot.handlers.start import router as start_router

routers = [
    start_router,
    search_router,
    offers_router,
]