import hashlib

from app.providers.embedding import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 8):
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than 0")

        self._dimensions = dimensions

    @property
    def model(self) -> str:
        return "fake-embedding-model"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("text cannot be empty")

        digest = hashlib.sha256(
            text.encode("utf-8")
        ).digest()

        vector: list[float] = []

        for index in range(self.dimensions):
            byte_value = digest[index % len(digest)]
            normalized = (byte_value / 255) * 2 - 1
            vector.append(round(normalized, 6))

        return vector