# app/services/chat_service.py

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

        for round_number in range(max_tool_rounds):
            logger.info(
                "LLM round started | round=%s",
                round_number + 1,
            )

            response = self.llm_provider.generate(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=self.tool_executor.definitions(),
            )

            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                return ChatResponse(
                    answer=response.get("content", ""),
                    model=self.llm_provider.model,
                )

            assistant_message = {
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            }

            messages.append(assistant_message)

            for tool_call in tool_calls:
                tool_message = self._execute_tool(tool_call)
                messages.append(tool_message)

        return ChatResponse(
            answer=(
                "Tôi đã thực hiện quá nhiều bước xử lý công cụ "
                "nhưng chưa thể hoàn tất câu trả lời."
            ),
            model=self.llm_provider.model,
        )

    def _execute_tool(
        self,
        tool_call: dict[str, Any],
    ) -> dict[str, Any]:

        tool_call_id = tool_call["id"]
        function_data = tool_call["function"]

        tool_name = function_data["name"]
        raw_arguments = function_data.get("arguments", "{}")

        try:
            arguments = json.loads(raw_arguments)

            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be a JSON object")

        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Invalid tool arguments | tool=%s | error=%s",
                tool_name,
                str(exc),
            )

            return {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(
                    {
                        "success": False,
                        "error": "Invalid JSON arguments",
                    },
                    ensure_ascii=False,
                ),
            }

        result, trace = self.tool_executor.execute(
            name=tool_name,
            arguments=arguments,
            tool_call_id=tool_call_id,
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
                default=str,
            ),
        }

    async def stream(self, request: ChatRequest):
        async for chunk in self.llm_provider.stream(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            yield chunk