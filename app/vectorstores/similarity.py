# app/vectorstores/similarity.py

import math


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same dimensions"
        )

    if not vector_a or not vector_b:
        raise ValueError("Vectors cannot be empty")

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    norm_a = math.sqrt(
        sum(value * value for value in vector_a)
    )

    norm_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if norm_a == 0 or norm_b == 0:
        raise ValueError(
            "Zero vector is not allowed"
        )

    return dot_product / (norm_a * norm_b)