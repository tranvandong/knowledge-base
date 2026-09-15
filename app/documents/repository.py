from abc import ABC, abstractmethod

from app.documents.models import Document


class DocumentRepository(ABC):
    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Document]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        document_id: str,
    ) -> Document | None:
        pass

    @abstractmethod
    def list(
        self,
        limit: int = 20,
    ) -> list[Document]:
        pass