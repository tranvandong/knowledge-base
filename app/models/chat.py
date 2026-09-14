from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal[
        "system",
        "user",
        "assistant",
        "tool",
    ]

    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

    temperature: float = Field(
        default=0.2,
        ge=0,
        le=2,
    )

    max_tokens: int = Field(
        default=2000,
        gt=0,
    )


class ChatResponse(BaseModel):
    answer: str
    model: str