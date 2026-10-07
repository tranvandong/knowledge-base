import pytest

from app.documents.in_memory_repository import InMemoryDocumentRepository
from app.tools.errors import ToolNotFoundError
from app.tools.list_documents import ListDocumentsTool
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor


def test_unknown_tool_raises_error():
    repository = InMemoryDocumentRepository()
    tool = ListDocumentsTool(repository)

    registry = ToolRegistry()
    registry.register(tool)

    with pytest.raises(ToolNotFoundError):
        registry.execute(
            name="unknown_tool",
            arguments={},
        )
        

def test_executor_returns_failed_trace_for_unknown_tool():
    repository = InMemoryDocumentRepository()
    registry = ToolRegistry()

    executor = ToolExecutor(registry)

    result, trace = executor.execute(
        name="unknown_tool",
        arguments={},
        tool_call_id="call_404",
    )

    assert result is None
    assert trace.success is False
    assert trace.tool_name == "unknown_tool"
    assert trace.tool_call_id == "call_404"
    assert trace.trace_id is not None
    assert trace.error is not None
    assert trace.duration_ms >= 0