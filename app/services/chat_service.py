import json
from typing import Any

from app.models.chat import ChatRequest, ChatResponse
from app.providers.llm import LLMProvider
from app.tools.errors import ToolError
from app.tools.executor import ToolExecutor


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
                tool_name = tool_call["function"]["name"]
                tool_call_id = tool_call["id"]
                raw_arguments = tool_call["function"]["arguments"]

                tool_message = self._execute_tool_safely(
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                    raw_arguments=raw_arguments,
                )

                messages.append(tool_message)

            tool_round += 1

        raise RuntimeError(
            "Maximum tool calling rounds exceeded"
        )

    def _execute_tool_safely(
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

            result, trace = self.tool_executor.execute(
                name=tool_name,
                arguments=arguments,
            )
            print("TOOL TRACE:", trace.model_dump_json())

            return {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(
                    {
                        "success": True,
                        "result": result,
                    },
                    ensure_ascii=False,
                ),
            }

        except ToolError as exc:
            return {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(
                    {
                        "success": False,
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                ),
            }

        except Exception:
            return   {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(
                    {
                        "success": False,
                        "error": trace.error,
                    },
                    ensure_ascii=False,
                ),
            }