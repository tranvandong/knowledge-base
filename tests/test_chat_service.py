from unittest.mock import Mock

from app.models.chat import ChatRequest
from app.services.chat_service import ChatService
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


def test_invalid_tool_arguments():
    provider = Mock()
    executor = Mock(spec=ToolExecutor)

    service = ChatService(
        llm_provider=provider,
        tool_executor=executor,
    )

    tool_call = {
        "id": "call_123",
        "type": "function",
        "function": {
            "name": "search_documents",
            "arguments": '{"query": "remote work"',
        },
    }

    result = service._execute_tool(tool_call)

    assert result["role"] == "tool"
    assert result["tool_call_id"] == "call_123"

    assert "Invalid JSON arguments" in result["content"]
    executor.execute.assert_not_called()
    


def test_chat_stops_after_max_tool_rounds():
    provider = Mock()
    provider.model = "test-model"
    executor = Mock(spec=ToolExecutor)

    provider.generate.return_value = {
        "content": None,
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "list_documents",
                    "arguments": "{}",
                },
            }
        ],
    }

    executor.definitions.return_value = []
    executor.execute.return_value = (
        {"count": 3},
        Mock(
            success=True,
            result={"count": 3},
            trace_id="trace_123",
            error=None,
        ),
    )

    service = ChatService(
        llm_provider=provider,
        tool_executor=executor,
    )

    request = ChatRequest(
        messages=[
            {
                "role": "user",
                "content": "List documents",
            }
        ]
    )

    response = service.chat(request)

    assert "quá nhiều bước" in response.answer
    assert provider.generate.call_count == 5