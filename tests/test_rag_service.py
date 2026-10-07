from app.documents.chunks import DocumentChunk
from app.providers.fake_embedding import FakeEmbeddingProvider
from app.providers.llm import LLMProvider
from app.rag.prompt_builder import RAGPromptBuilder
from app.rag.service import RAGService
from app.search.models import SearchItem
from app.search.service import SemanticSearchService
from app.vectorstores.in_memory import InMemoryVectorStore


class FakeLLMProvider:
    model = "fake-llm"

    def chat(self, messages):
        return type(
            "FakeResponse",
            (),
            {
                "content": "Remote work policy answer",
            },
        )()

def make_chunk(
    chunk_id: str,
    content: str,
    embedding: list[float],
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        chunk_index=0,
        embedding=embedding,
        metadata={
            "title": "Test Document",
        },
    )


def test_rag_service_returns_answer():
    vector_store = InMemoryVectorStore()
    embedding_provider = FakeEmbeddingProvider(dimensions=8)
    vector_store.add(
        [
            make_chunk(
                "chunk_001",
                "Remote work policy",
                embedding_provider.embed("remote work policy"),
            ),
            make_chunk(
                "chunk_002",
                "Company handbook",
                embedding_provider.embed("company handbook"),
            ),
        ]
    )
    fake_llm = FakeLLMProvider()
    
    similarity_threshold = 0.7
    search_service = SemanticSearchService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        similarity_threshold=similarity_threshold,
    )
    
    prompt_builder = RAGPromptBuilder()
    rag_service = RAGService(
        search_service=search_service,
        prompt_builder=prompt_builder,
        llm_provider=fake_llm,
    )
    response = rag_service.answer(
        query="remote work policy",
        top_k=1,
    )
    
    assert response.query == "remote work policy"
    assert len(response.sources) == 1
    assert response.sources[0].chunk_id == "chunk_001"
    assert response.sources[0].score > 0
    assert response.sources[0].score > similarity_threshold
    

def test_rag_service_not_found_document():
    vector_store=InMemoryVectorStore()
    embedding_provider = FakeEmbeddingProvider(dimensions=8)
    vector_store.add(
            [
                make_chunk(
                    "chunk_001",
                    "Remote work policy",
                    embedding_provider.embed("remote work policy"),
                ),
                make_chunk(
                    "chunk_002",
                    "Company handbook",
                    embedding_provider.embed("company handbook"),
                ),
            ]
        )
    search_results = vector_store.search(
        query_embedding=embedding_provider.embed("salary policy"),
        top_k=1,
    )
    fake_llm = FakeLLMProvider()
    search_service = SemanticSearchService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    prompt_builder = RAGPromptBuilder()
    rag_service = RAGService(
        search_service=search_service,
        prompt_builder=prompt_builder,
        llm_provider=fake_llm,
    )
    response = rag_service.answer(
        query="salary policy",
        top_k=1,
    )
    
    assert response.query == "salary policy"
    assert len(response.sources) == 0
    assert search_results[0].score < 0.7