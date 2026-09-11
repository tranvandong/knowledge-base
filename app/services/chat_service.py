from app.models.chat import ChatRequest, ChatResponse
from app.providers.llm import LLMProvider


class ChatService:

    def __init__(
        self,
        llm_provider: LLMProvider,
    ):
        self.llm_provider = llm_provider

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        answer = self.llm_provider.generate(
            request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ChatResponse(
            answer=answer,
            model=self.llm_provider.model,
        )
    
    async def stream(self, request):

        async for chunk in self.llm_provider.stream(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            yield chunk