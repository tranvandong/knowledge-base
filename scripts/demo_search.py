from app.documents.chunker import TextChunker
from app.documents.embedding_service import DocumentEmbeddingService
from app.documents.in_memory_repository import InMemoryDocumentRepository
from app.providers.fake_embedding import FakeEmbeddingProvider
from app.search.service import SemanticSearchService
from app.vectorstores.in_memory import InMemoryVectorStore


repository = InMemoryDocumentRepository()
document = repository.get_by_id("doc_003")

if document is None:
    raise RuntimeError("Document not found")

chunker = TextChunker(
    chunk_size=120,
    overlap=20,
)

chunks = chunker.split(document)

embedding_provider = FakeEmbeddingProvider(dimensions=8)

embedding_service = DocumentEmbeddingService(
    embedding_provider
)

embedded_chunks = embedding_service.embed_chunks(chunks)

vector_store = InMemoryVectorStore()
vector_store.add(embedded_chunks)

search_service = SemanticSearchService(
    embedding_provider=embedding_provider,
    vector_store=vector_store,
)

response = search_service.search(
    query="remote work",
    top_k=3,
)

for item in response.results:
    print(f"Score: {item.score:.2f}")
    print(f"Chunk: {item.chunk_id}")
    print(item.content)
    print("---")