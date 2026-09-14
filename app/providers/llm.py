from abc import ABC, abstractmethod
from typing import Any

from app.models.chat import ChatMessage
from collections.abc import AsyncIterator


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages,
        temperature,
        max_tokens,
    ) -> AsyncIterator[str]:
        pass