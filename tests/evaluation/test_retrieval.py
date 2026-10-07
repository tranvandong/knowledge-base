from app.evaluation.retrieval import hit_at_k
from app.search.models import SearchItem


def make_result(chunk_id: str) -> SearchItem:
    return SearchItem(
        chunk_id=chunk_id,
        document_id="doc-1",
        content="test",
        score=0.9,
        metadata={},
    )


def test_hit_at_k_when_expected_chunk_is_found():

    results = [
        make_result("chunk-1"),
        make_result("chunk-2"),
        make_result("chunk-3"),
    ]

    assert hit_at_k(
        results=results,
        expected_chunk_ids=["chunk-2"],
        k=3,
    )


def test_hit_at_k_when_expected_chunk_is_not_found():

    results = [
        make_result("chunk-1"),
        make_result("chunk-2"),
    ]

    assert not hit_at_k(
        results=results,
        expected_chunk_ids=["chunk-3"],
        k=2,
    )


def test_hit_at_k_respects_k():

    results = [
        make_result("chunk-1"),
        make_result("chunk-2"),
        make_result("chunk-3"),
    ]

    assert not hit_at_k(
        results=results,
        expected_chunk_ids=["chunk-3"],
        k=2,
    )


def test_multiple_expected_chunks():

    results = [
        make_result("chunk-1"),
        make_result("chunk-2"),
    ]

    assert hit_at_k(
        results=results,
        expected_chunk_ids=[
            "chunk-2",
            "chunk-3",
        ],
        k=2,
    )