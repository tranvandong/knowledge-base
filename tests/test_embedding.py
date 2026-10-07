import pytest

from app.providers.fake_embedding import FakeEmbeddingProvider


def test_embed_returns_expected_dimensions():
    provider = FakeEmbeddingProvider(dimensions=8)

    vector = provider.embed("remote work policy")

    assert len(vector) == 8
    assert all(isinstance(value, float) for value in vector)


def test_embed_many_returns_multiple_vectors():
    provider = FakeEmbeddingProvider(dimensions=4)

    vectors = provider.embed_many(
        [
            "remote work",
            "company handbook",
            "employee policy",
        ]
    )

    assert len(vectors) == 3
    assert all(len(vector) == 4 for vector in vectors)


def test_empty_text_is_rejected():
    provider = FakeEmbeddingProvider()

    with pytest.raises(ValueError):
        provider.embed("   ")


def test_invalid_dimensions_are_rejected():
    with pytest.raises(ValueError):
        FakeEmbeddingProvider(dimensions=0)
        
        
from app.documents.chunks import DocumentChunk
from app.documents.embedding_service import DocumentEmbeddingService


def test_embed_chunks_attaches_embeddings():
    provider = FakeEmbeddingProvider(dimensions=4)
    service = DocumentEmbeddingService(provider)

    chunks = [
        DocumentChunk(
            chunk_id="chunk_001",
            document_id="doc_001",
            content="Remote work policy",
            chunk_index=0,
        ),
        DocumentChunk(
            chunk_id="chunk_002",
            document_id="doc_001",
            content="Manager approval is required",
            chunk_index=1,
        ),
    ]

    result = service.embed_chunks(chunks)

    assert len(result) == 2
    assert result[0].embedding is not None
    assert result[1].embedding is not None
    assert len(result[0].embedding) == 4
    assert len(result[1].embedding) == 4

    # Đảm bảo object gốc không bị thay đổi
    assert chunks[0].embedding is None