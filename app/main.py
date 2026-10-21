from fastapi import FastAPI

from app.ai.chat import router as chat_router
from app.ai.embedding import router as embedding_router
from app.ai.health import router as health_router
from app.ai.ocr import router as ocr_router
from app.logging_config import setup_logging


setup_logging()


app = FastAPI(
    title="AI Service",
    version="0.1.0",
    description="AI Service - Chat, Embedding, OCR",
)

app.include_router(chat_router)
app.include_router(embedding_router)
app.include_router(health_router)
app.include_router(ocr_router)


