from app.models.embedding import EmbeddingRequest, EmbeddingResponse


class EmbeddingService:
    def  embed(sefl, request: EmbeddingRequest) -> EmbeddingResponse:
        return  EmbeddingResponse(embedding=[], dimenssion=0, model="text-embedding-ada-002")