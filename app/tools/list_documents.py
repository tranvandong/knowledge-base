from typing import Any

from pydantic import BaseModel, Field

from app.documents.repository import DocumentRepository
from app.tools.base import BaseTool


class ListDocumentsInput(BaseModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of documents to return",
    )


class ListDocumentsTool(BaseTool[ListDocumentsInput]):
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    @property
    def name(self) -> str:
        return "list_documents"

    @property
    def description(self) -> str:
        return "List documents currently available in the knowledge base."

    @property
    def input_model(self) -> type[ListDocumentsInput]:
        return ListDocumentsInput

    def execute(
        self,
        arguments: ListDocumentsInput,
    ) -> dict[str, Any]:
        documents = self.repository.list(
            limit=arguments.limit
        )

        return {
            "count": len(documents),
            "documents": [
                {
                    "document_id": document.document_id,
                    "title": document.title,
                    "page": document.page,
                }
                for document in documents
            ],
        }