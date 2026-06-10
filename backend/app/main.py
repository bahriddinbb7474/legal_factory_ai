from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.api.chats import router as chats_router
from app.api.health import router as health_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(agents_router)
app.include_router(chats_router)
