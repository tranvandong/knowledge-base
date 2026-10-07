from app.documents.in_memory_repository import InMemoryDocumentRepository
from app.tools.list_documents import ListDocumentsTool


def test_list_documents_success():
    repository = InMemoryDocumentRepository()
    tool = ListDocumentsTool(repository)

    result = tool.execute(
        tool.input_model(limit=10)
    )

    assert result["count"] == 3
    assert len(result["documents"]) == 3