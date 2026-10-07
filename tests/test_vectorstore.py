import pytest

from app.documents.chunks import DocumentChunk
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
    )


def test_add_and_count_chunks():
    store = InMemoryVectorStore()

    chunks = [
        make_chunk(
            "chunk_001",
            "Remote work policy",
            [1.0, 0.0],
        ),
        make_chunk(
            "chunk_002",
            "Company handbook",
            [0.0, 1.0],
        ),
    ]

    store.add(chunks)

    assert store.count() == 2


def test_search_returns_most_similar_chunk_first():
    store = InMemoryVectorStore()

    store.add(
        [
            make_chunk(
                "chunk_001",
                "Remote work policy",
                [1.0, 0.0],
            ),
            make_chunk(
                "chunk_002",
                "Company handbook",
                [0.0, 1.0],
            ),
        ]
    )

    results = store.search(
        query_embedding=[0.9, 0.1],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk.chunk_id == "chunk_001"
    assert results[0].score > 0


def test_chunk_without_embedding_is_rejected():
    store = InMemoryVectorStore()

    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content="No embedding",
        chunk_index=0,
    )

    with pytest.raises(ValueError):
        store.add([chunk])


def test_invalid_top_k_is_rejected():
    store = InMemoryVectorStore()

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[1.0, 0.0],
            top_k=0,
        )