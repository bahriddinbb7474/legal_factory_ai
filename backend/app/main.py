from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.agents import router as agents_router
from app.api.chats import router as chats_router
from app.api.documents import chat_router as chat_documents_router
from app.api.documents import router as documents_router
from app.api.generated_documents import router as generated_documents_router
from app.api.health import router as health_router
from app.api.legal_sources import router as legal_sources_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(agents_router)
app.include_router(chats_router)
app.include_router(documents_router)
app.include_router(chat_documents_router)
app.include_router(generated_documents_router)
app.include_router(legal_sources_router)
app.include_router(admin_router)
