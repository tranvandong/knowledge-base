from openai import OpenAI

from app.models.chat import ChatMessage
from app.providers.llm import LLMProvider


class KiloProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.kilo.ai/api/gateway",
        )

        self.model = model

    def generate(
        self,
        messages: list[ChatMessage],
        temperature,
        max_tokens,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""
    
    async def stream(
    self,
    messages,
    temperature,
    max_tokens,
    ):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in response:
            content = chunk.choices[0].delta.content

            if content:
                yield content