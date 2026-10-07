from app.providers.embedding import EmbeddingProvider
from app.vectorstores.in_memory import InMemoryVectorStore
from app.search.models import SearchItem, SemanticSearchResponse


class SemanticSearchService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: InMemoryVectorStore,
        similarity_threshold: float = 0.0,
    ):
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(
                "similarity_threshold must be between 0 and 1"
            )

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.similarity_threshold = similarity_threshold

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> SemanticSearchResponse:

        query = query.strip()

        if not query:
            raise ValueError("query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        query_embedding = self.embedding_provider.embed(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )
        
        results = [
            result
            for result in results
            if result.score >= self.similarity_threshold
        ]

        items = [
            SearchItem(
                chunk_id=result.chunk.chunk_id,
                document_id=result.chunk.document_id,
                content=result.chunk.content,
                score=result.score,
                metadata=result.chunk.metadata,
            )
            for result in results
        ]

        return SemanticSearchResponse(
            query=query,
            results=items,
        )