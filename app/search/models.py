from pydantic import BaseModel


class SearchItem(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, str | int | float | bool | None]


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SearchItem]