from app.documents.chunks import DocumentChunk
from app.providers.embedding import EmbeddingProvider


class DocumentEmbeddingService:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def embed_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        texts = [chunk.content for chunk in chunks]
        vectors = self.provider.embed_many(texts)

        if len(vectors) != len(chunks):
            raise ValueError(
                "Number of embeddings must match number of chunks"
            )

        embedded_chunks: list[DocumentChunk] = []

        for chunk, vector in zip(chunks, vectors):
            embedded_chunks.append(
                chunk.model_copy(
                    update={
                        "embedding": vector,
                    }
                )
            )

        return embedded_chunks