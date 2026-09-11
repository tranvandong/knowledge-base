from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

    temperature: float = Field(
        default=0.2,
        ge=0,
        le=2,
    )

    max_tokens: int = Field(
        default=1000,
        gt=0,
    )


class ChatResponse(BaseModel):
    answer: str
    model: str