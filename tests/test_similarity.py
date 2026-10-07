import pytest

from app.vectorstores.similarity import cosine_similarity


def test_identical_vectors_have_similarity_one():
    result = cosine_similarity(
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    )

    assert result == pytest.approx(1.0)


def test_orthogonal_vectors_have_similarity_zero():
    result = cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    )

    assert result == pytest.approx(0.0)


def test_different_dimensions_are_rejected():
    with pytest.raises(ValueError):
        cosine_similarity(
            [1.0, 2.0],
            [1.0, 2.0, 3.0],
        )


def test_zero_vector_is_rejected():
    with pytest.raises(ValueError):
        cosine_similarity(
            [0.0, 0.0],
            [1.0, 2.0],
        )