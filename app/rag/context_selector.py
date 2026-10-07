from app.search.models import SearchItem


class ContextSelector:
    def __init__(
        self,
        max_context_chars: int = 6000,
    ):
        if max_context_chars <= 0:
            raise ValueError(
                "max_context_chars must be greater than 0"
            )

        self.max_context_chars = max_context_chars

    def select(
        self,
        results: list[SearchItem],
    ) -> list[SearchItem]:

        selected: list[SearchItem] = []
        current_length = 0

        for result in results:
            content_length = len(result.content)

            if current_length + content_length > self.max_context_chars:
                break

            selected.append(result)
            current_length += content_length

        return selected