import json
import logging
from typing import Any

from app.models.chat import ChatRequest, ChatResponse
from app.providers.llm import LLMProvider
from app.tools.executor import ToolExecutor


logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        llm_provider: LLMProvider,
        tool_executor: ToolExecutor,
    ):
        self.llm_provider = llm_provider
        self.tool_executor = tool_executor

    def chat(self, request: ChatRequest) -> ChatResponse:
        messages: list[dict[str, Any]] = [
            message.model_dump(exclude_none=True)
            for message in request.messages
        ]

        max_tool_rounds = 5
        tool_round = 0

        while tool_round < max_tool_rounds:
            response = self.llm_provider.generate(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=self.tool_executor.definitions(),
            )

            if response["type"] == "final":
                return ChatResponse(
                    answer=response["content"],
                    model=self.llm_provider.model,
                )

            if response["type"] != "tool_call":
                raise ValueError(
                    f"Unsupported response type: {response['type']}"
                )

            tool_calls = response["tool_calls"]

            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:
                tool_call_id = tool_call["id"]
                tool_name = tool_call["function"]["name"]
                raw_arguments = tool_call["function"]["arguments"]

                tool_message = self._execute_tool(
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                    raw_arguments=raw_arguments,
                )

                messages.append(tool_message)

            tool_round += 1

        raise RuntimeError(
            "Maximum tool calling rounds exceeded"
        )

    def _execute_tool(
        self,
        tool_name: str,
        tool_call_id: str,
        raw_arguments: str,
    ) -> dict[str, Any]:
        try:
            arguments = json.loads(raw_arguments)

            if not isinstance(arguments, dict):
                raise ValueError(
                    "Tool arguments must be a JSON object"
                )

        except json.JSONDecodeError:
            return {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(
                    {
                        "success": False,
                        "error": "Invalid JSON tool arguments",
                    },
                    ensure_ascii=False,
                ),
            }

        result, trace = self.tool_executor.execute(
            name=tool_name,
            arguments=arguments,
            tool_call_id=tool_call_id,
        )

        logger.info(
            "Tool trace | %s",
            trace.model_dump_json(),
        )

        if trace.success:
            content = {
                "success": True,
                "result": result,
                "trace_id": str(trace.trace_id),
            }
        else:
            content = {
                "success": False,
                "error": trace.error,
                "trace_id": str(trace.trace_id),
            }

        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(
                content,
                ensure_ascii=False,
            ),
        }