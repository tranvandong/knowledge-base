from dataclasses import dataclass

from app.documents.chunks import DocumentChunk
from app.vectorstores.similarity import cosine_similarity


@dataclass
class SearchResult:
    chunk: DocumentChunk
    score: float


class InMemoryVectorStore:
    def __init__(self):
        self._chunks: list[DocumentChunk] = []

    def add(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            if chunk.embedding is None:
                raise ValueError(
                    f"Chunk '{chunk.chunk_id}' has no embedding"
                )

        self._chunks.extend(chunks)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        results: list[SearchResult] = []

        for chunk in self._chunks:
            if chunk.embedding is None:
                continue

            score = cosine_similarity(
                query_embedding,
                chunk.embedding,
            )

            results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]

    def count(self) -> int:
        return len(self._chunks)