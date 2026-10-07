from app.rag.context_selector import ContextSelector
from app.search.models import SearchItem


def make_result(
    chunk_id: str,
    content: str,
) -> SearchItem:
    return SearchItem(
        chunk_id=chunk_id,
        document_id="doc-1",
        content=content,
        score=0.9,
        metadata={},
    )


def test_select_results_within_context_budget():
    selector = ContextSelector(
        max_context_chars=100,
    )

    results = [
        make_result("chunk-1", "A" * 40),
        make_result("chunk-2", "B" * 40),
        make_result("chunk-3", "C" * 40),
    ]

    selected = selector.select(results)

    assert len(selected) == 2
    assert selected[0].chunk_id == "chunk-1"
    assert selected[1].chunk_id == "chunk-2"


def test_large_chunk_is_not_partially_included():
    selector = ContextSelector(
        max_context_chars=100,
    )

    results = [
        make_result("chunk-1", "A" * 80),
        make_result("chunk-2", "B" * 50),
    ]

    selected = selector.select(results)

    assert len(selected) == 1
    assert selected[0].chunk_id == "chunk-1"


def test_empty_results():
    selector = ContextSelector(
        max_context_chars=100,
    )

    selected = selector.select([])

    assert selected == []


def test_invalid_context_budget():
    try:
        ContextSelector(max_context_chars=0)
        assert False
    except ValueError as error:
        assert str(error) == (
            "max_context_chars must be greater than 0"
        )