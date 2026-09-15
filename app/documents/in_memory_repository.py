from app.documents.models import Document
from app.documents.repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self.documents = [
            Document(
                document_id="doc_001",
                title="HR Policy",
                content="Nhân viên được nghỉ 12 ngày phép năm.",
                page=12,
            ),
            Document(
                document_id="doc_002",
                title="Company Handbook",
                content="Nhân viên cần gửi đơn nghỉ phép cho quản lý.",
                page=8,
            ),
            Document(
                document_id="doc_003",
                title="Remote Work Policy",
                content="Nhân viên có thể làm việc từ xa theo quy định.",
                page=15,
            ),
        ]

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Document]:
        normalized_query = query.lower()

        results = [
            document
            for document in self.documents
            if normalized_query in document.title.lower()
            or normalized_query in document.content.lower()
        ]

        return results[:limit]

    def get_by_id(
        self,
        document_id: str,
    ) -> Document | None:
        return next(
            (
                document
                for document in self.documents
                if document.document_id == document_id
            ),
            None,
        )

    def list(
        self,
        limit: int = 20,
    ) -> list[Document]:
        return self.documents[:limit]