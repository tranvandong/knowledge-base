from typing import Any

from pydantic import BaseModel, Field

from app.documents.repository import DocumentRepository
from app.tools.base import BaseTool


class SearchDocumentsInput(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural language query used to search documents",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of documents to return",
    )


class SearchDocumentsTool(BaseTool[SearchDocumentsInput]):
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    @property
    def name(self) -> str:
        return "search_documents"

    @property
    def description(self) -> str:
        return "Search documents in the knowledge base."

    @property
    def input_model(self) -> type[SearchDocumentsInput]:
        return SearchDocumentsInput

    def execute(
        self,
        arguments: SearchDocumentsInput,
    ) -> dict[str, Any]:
        documents = self.repository.search(
            query=arguments.query,
            limit=arguments.limit,
        )

        return {
            "query": arguments.query,
            "results": [
                document.model_dump()
                for document in documents
            ],
        }