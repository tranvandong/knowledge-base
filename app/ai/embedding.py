from fastapi import APIRouter

from app.models.embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
)
from app.services.embedding_service import EmbeddingService


router = APIRouter(
    prefix="/embed",
    tags=["Embedding"],
)

embedding_service = EmbeddingService()


@router.post("", response_model=EmbeddingResponse)
def embed(request: EmbeddingRequest):
    return embedding_service.embed(request)