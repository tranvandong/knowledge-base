from app.providers.llm import LLMProvider
from app.rag.context_selector import ContextSelector
from app.search.service import SemanticSearchService
from app.rag.prompt_builder import RAGPromptBuilder
from app.rag.models import RAGResponse


class RAGService:
    def __init__(
        self,
        search_service: SemanticSearchService,
        prompt_builder: RAGPromptBuilder,
        context_selector: ContextSelector,
        llm_provider: LLMProvider
    ):
        self.search_service = search_service
        self.prompt_builder = prompt_builder
        self.context_selector = context_selector
        self.llm_provider = llm_provider

    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> RAGResponse:

        search_response = self.search_service.search(
            query=query,
            top_k=top_k,
        )

        selected_results = self.context_selector.select(
            search_response.results,
        )

        messages = self.prompt_builder.build_messages(
            query=query,
            results=selected_results,
        )

        response = self.llm_provider.chat(messages)

        return RAGResponse(
            query=query,
            answer=response.content,
            sources=search_response.results,
        )