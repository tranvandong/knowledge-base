from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]