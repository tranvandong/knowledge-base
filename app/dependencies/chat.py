from fastapi import Depends

from app.config import settings
from app.documents.in_memory_repository import InMemoryDocumentRepository
from app.documents.repository import DocumentRepository
from app.providers.kilo_llm import KiloProvider
from app.providers.llm import LLMProvider
from app.services.chat_service import ChatService
from app.tools.executor import ToolExecutor
from app.tools.get_document import GetDocumentTool
from app.tools.list_documents import ListDocumentsTool
from app.tools.registry import ToolRegistry
from app.tools.search_documents import SearchDocumentsTool


def get_llm_provider() -> LLMProvider:
    return KiloProvider(
        api_key=settings.kilo_api_key,
        model=settings.kilo_model,
    )


def get_document_repository() -> DocumentRepository:
    return InMemoryDocumentRepository()


def get_tool_executor(
    repository: DocumentRepository = Depends(get_document_repository),
) -> ToolExecutor:
    registry = ToolRegistry()

    registry.register(SearchDocumentsTool(repository))
    registry.register(GetDocumentTool(repository))
    registry.register(ListDocumentsTool(repository))

    return ToolExecutor(registry)


def get_chat_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
    tool_executor: ToolExecutor = Depends(get_tool_executor),
) -> ChatService:
    return ChatService(
        llm_provider=llm_provider,
        tool_executor=tool_executor,
    )