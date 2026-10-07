from app.rag.prompt_builder import RAGPromptBuilder
from app.search.models import SearchItem


def make_result(content: str) -> SearchItem:
    return SearchItem(
        chunk_id="chunk-1",
        document_id="doc-1",
        content=content,
        score=0.9,
        metadata={},
    )


def test_build_context_contains_source_information():
    builder = RAGPromptBuilder()

    context = builder.build_context(
        [make_result("Python is a programming language.")]
    )

    assert "document_id: doc-1" in context
    assert "chunk_id: chunk-1" in context
    assert "Python is a programming language." in context


def test_build_messages_returns_system_and_user_messages():
    builder = RAGPromptBuilder()

    messages = builder.build_messages(
        query="What is Python?",
        results=[make_result("Python is a programming language.")],
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "What is Python?" in messages[1]["content"]


def test_empty_query_is_rejected():
    builder = RAGPromptBuilder()

    try:
        builder.build_messages(query="   ", results=[])
        assert False
    except ValueError as error:
        assert str(error) == "query cannot be empty"


def test_empty_results_are_supported():
    builder = RAGPromptBuilder()

    context = builder.build_context([])

    assert context == "No relevant documents were found."


def test_context_is_limited():
    builder = RAGPromptBuilder(max_context_chars=100)

    context = builder.build_context(
        [make_result("A" * 1000)]
    )

    assert len(context) <= 100