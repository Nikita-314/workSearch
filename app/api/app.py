from fastapi import FastAPI

from app.api.routes.redirect import router as redirect_router

api_app = FastAPI(title="workSearch API")

api_app.include_router(redirect_router)