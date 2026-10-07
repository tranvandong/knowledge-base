from app.documents.chunks import DocumentChunk
from app.providers.fake_embedding import FakeEmbeddingProvider
from app.search.service import SemanticSearchService
from app.vectorstores.in_memory import InMemoryVectorStore


def make_chunk(
    chunk_id: str,
    content: str,
    embedding: list[float],
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        chunk_index=0,
        embedding=embedding,
        metadata={
            "title": "Test Document",
        },
    )


def test_semantic_search_returns_results():
    provider = FakeEmbeddingProvider(dimensions=8)
    store = InMemoryVectorStore()

    store.add(
        [
            make_chunk(
                "chunk_001",
                "Remote work policy",
                provider.embed("remote work policy"),
            ),
            make_chunk(
                "chunk_002",
                "Company handbook",
                provider.embed("company handbook"),
            ),
        ]
    )

    service = SemanticSearchService(
        embedding_provider=provider,
        vector_store=store,
    )

    response = service.search(
        query="remote work policy",
        top_k=1,
    )

    assert response.query == "remote work policy"
    assert len(response.results) == 1
    assert response.results[0].chunk_id == "chunk_001"
    assert response.results[0].score > 0


def test_empty_query_is_rejected():
    provider = FakeEmbeddingProvider()
    store = InMemoryVectorStore()

    service = SemanticSearchService(provider, store)

    try:
        service.search("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "query cannot be empty"