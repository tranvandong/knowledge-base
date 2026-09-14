from typing import Any

from pydantic import BaseModel, Field

from app.tools.base import BaseTool


class SearchDocumentsInput(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class SearchDocumentsTool(BaseTool):
    name = "search_documents"

    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": (
                    "Search documents in the knowledge base "
                    "using a natural language query."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The document search query",
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        }
        

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        data = SearchDocumentsInput.model_validate(arguments)

        # Mock data.
        # Sau này thay bằng PostgreSQL + pgvector.
        documents = [
            {
                "document_id": "doc_001",
                "title": "HR Policy",
                "content": "Nhân viên được nghỉ 12 ngày phép năm.",
                "page": 12,
            },
            {
                "document_id": "doc_002",
                "title": "Company Handbook",
                "content": "Nhân viên cần gửi đơn nghỉ phép cho quản lý.",
                "page": 8,
            },
        ]

        return {
            "query": data.query,
            "results": documents[: data.limit],
        }