from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )
    embedding: list[float] | None = None