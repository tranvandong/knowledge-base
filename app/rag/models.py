from pydantic import BaseModel

from app.search.models import SearchItem


class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: list[SearchItem]