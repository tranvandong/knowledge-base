import json
from typing import Any

from app.models.chat import ChatRequest, ChatResponse
from app.providers.llm import LLMProvider
from app.tools.registry import ToolRegistry


class ChatService:

    def __init__(
        self,
        llm_provider: LLMProvider,
        tool_registry: ToolRegistry,
    ):
        self.llm_provider = llm_provider
        self.tool_registry = tool_registry

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
                tools=self.tool_registry.definitions(),
            )

            if response["type"] == "final":
                return ChatResponse(
                    answer=response["content"],
                    model=self.llm_provider.model,
                )

            if response["type"] != "tool_call":
                raise ValueError(
                    f"Unsupported LLM response type: {response['type']}"
                )

            tool_calls = response["tool_calls"]

            # Giữ nguyên assistant message theo OpenAI-compatible format
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                raw_arguments = tool_call["function"]["arguments"]

                try:
                    tool_arguments = json.loads(raw_arguments)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid tool arguments for {tool_name}: "
                        f"{raw_arguments}"
                    ) from exc

                tool_result = self.tool_registry.execute(
                    name=tool_name,
                    arguments=tool_arguments,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(
                            tool_result,
                            ensure_ascii=False,
                        ),
                    }
                )

            tool_round += 1

        raise RuntimeError("Maximum tool calling rounds exceeded")

    def _to_chat_message(
        self,
        message: dict[str, Any],
    ):
        """
        Chuyển dict nội bộ về ChatMessage.
        Tool message cần được truyền đúng role/content.
        """
        from app.models.chat import ChatMessage

        return ChatMessage.model_validate(message)
    
    
    async def stream(self, request):

        async for chunk in self.llm_provider.stream(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            yield chunk