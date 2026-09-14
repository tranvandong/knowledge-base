import json
from typing import Any

from openai import OpenAI

from app.models.chat import ChatMessage
from app.providers.llm import LLMProvider


class KiloProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.kilo.ai/api/gateway",
        )

        self.model = model

    def generate(
        self,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**payload)
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_calls = []

            for tool_call in message.tool_calls:
                tool_calls.append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                )

            return {
                "type": "tool_call",
                "tool_calls": tool_calls,
            }

        # LLM trả câu trả lời cuối cùng
        return {
            "type": "final",
            "content": message.content or "",
        }
        
    
    async def stream(
    self,
    messages,
    temperature,
    max_tokens,
    ):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in response:
            content = chunk.choices[0].delta.content

            if content:
                yield content