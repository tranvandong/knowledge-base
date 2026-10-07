# tests/test_chunker.py

import pytest

from app.documents.chunker import TextChunker
from app.documents.models import Document


def test_chunk_document():
    document = Document(
        document_id="doc_001",
        title="Test Document",
        content="abcdefghij",
    )

    chunker = TextChunker(
        chunk_size=4,
        overlap=1,
    )

    chunks = chunker.split(document)

    assert len(chunks) == 4
    assert chunks[0].content == "abcd"
    assert chunks[1].content == "defg"
    assert chunks[2].content == "ghij"
    assert chunks[3].content == "j"


def test_empty_document_returns_empty_chunks():
    document = Document(
        document_id="doc_empty",
        title="Empty",
        content="   ",
    )

    chunker = TextChunker()

    assert chunker.split(document) == []


def test_invalid_chunk_configuration():
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, overlap=100)

    with pytest.raises(ValueError):
        TextChunker(chunk_size=0)

    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, overlap=-1)