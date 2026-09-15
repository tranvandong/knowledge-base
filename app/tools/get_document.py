from typing import Any

from pydantic import BaseModel, Field

from app.documents.repository import DocumentRepository
from app.tools.base import BaseTool


class GetDocumentInput(BaseModel):
    document_id: str = Field(
        min_length=1,
        description="The unique ID of the document to retrieve",
    )


class GetDocumentTool(BaseTool[GetDocumentInput]):
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    @property
    def name(self) -> str:
        return "get_document"

    @property
    def description(self) -> str:
        return "Retrieve a document by its document ID."

    @property
    def input_model(self) -> type[GetDocumentInput]:
        return GetDocumentInput

    def execute(
        self,
        arguments: GetDocumentInput,
    ) -> dict[str, Any]:
        document = self.repository.get_by_id(
            arguments.document_id
        )

        if document is None:
            return {
                "found": False,
                "document_id": arguments.document_id,
            }

        return {
            "found": True,
            "document": document.model_dump(),
        }