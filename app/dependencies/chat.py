from fastapi import Depends

from app.config import settings
from app.providers.kilo_llm import KiloProvider
from app.providers.llm import LLMProvider
from app.services.chat_service import ChatService
from app.tools.registry import ToolRegistry
from app.tools.search_documents import SearchDocumentsTool


def get_llm_provider() -> LLMProvider:
    return KiloProvider(
        api_key=settings.kilo_api_key,
        model=settings.kilo_model,
    )
    
    
def get_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(SearchDocumentsTool())
    return registry


def get_chat_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> ChatService:
    return ChatService(
        llm_provider,
        tool_registry
    )