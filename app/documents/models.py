from pydantic import BaseModel


class Document(BaseModel):
    document_id: str
    title: str
    content: str
    page: int | None = None