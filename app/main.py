from fastapi import FastAPI

from app.ai.chat import router as chat_router
from app.ai.embedding import router as embedding_router
from app.ai.health import router as health_router

app = FastAPI(
    title="AI Service",
    version="0.1.0",
    description="AI Service",
)

app.include_router(chat_router)
app.include_router(embedding_router)
app.include_router(health_router)



