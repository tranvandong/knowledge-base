from fastapi import Depends

from app.config import settings
from app.providers.kilo_llm import KiloProvider
from app.providers.llm import LLMProvider
from app.services.chat_service import ChatService


def get_llm_provider() -> LLMProvider:
    return KiloProvider(
        api_key=settings.kilo_api_key,
        model=settings.kilo_model,
    )


def get_chat_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> ChatService:
    return ChatService(llm_provider)