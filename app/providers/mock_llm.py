from app.providers.llm import LLMProvider


class MockLLMProvider(LLMProvider):

    def generate(self, message: str) -> str:
        return f"Mock response: {message}"