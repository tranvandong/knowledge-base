from pydantic import BaseModel

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: list[float]
    dimenssion: int
    model: str