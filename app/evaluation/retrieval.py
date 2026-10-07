from app.search.models import SearchItem


def hit_at_k(
    results: list[SearchItem],
    expected_chunk_ids: list[str],
    k: int,
) -> bool:

    if k <= 0:
        raise ValueError("k must be greater than 0")

    if not expected_chunk_ids:
        raise ValueError(
            "expected_chunk_ids cannot be empty"
        )

    retrieved_ids = {
        result.chunk_id
        for result in results[:k]
    }

    return any(
        chunk_id in retrieved_ids
        for chunk_id in expected_chunk_ids
    )
    

def precision_at_k(
    results: list[SearchItem],
    expected_chunk_ids: list[str],
    k: int,
) -> float:

    if k <= 0:
        raise ValueError("k must be greater than 0")

    if not expected_chunk_ids:
        raise ValueError(
            "expected_chunk_ids cannot be empty"
        )

    retrieved = results[:k]

    relevant_count = sum(
        1
        for result in retrieved
        if result.chunk_id in expected_chunk_ids
    )

    return relevant_count / len(retrieved) if retrieved else 0.0


def recall_at_k(
    results: list[SearchItem],
    expected_chunk_ids: list[str],
    k: int,
) -> float:

    if k <= 0:
        raise ValueError("k must be greater than 0")

    if not expected_chunk_ids:
        raise ValueError(
            "expected_chunk_ids cannot be empty"
        )

    retrieved_ids = {
        result.chunk_id
        for result in results[:k]
    }

    relevant_retrieved = sum(
        1
        for chunk_id in expected_chunk_ids
        if chunk_id in retrieved_ids
    )

    return relevant_retrieved / len(expected_chunk_ids)