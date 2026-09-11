from abc import ABC, abstractmethod

from app.models.chat import ChatMessage
from collections.abc import AsyncIterator


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        messages: list[ChatMessage],
        temperature: float,
        max_tokens: int,
    ) -> str:
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages,
        temperature,
        max_tokens,
    ) -> AsyncIterator[str]:
        pass