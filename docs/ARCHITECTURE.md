# System Architecture

## High-Level Architecture

```
                                    ┌──────────────────────────────────────────┐
                                    │              FastAPI App                   │
                                    │            (app/main.py)                  │
                                    └──────────────────────────────────────────┘
                                                       │
                       ┌───────────────────────────────┼───────────────────────────────┐
                       │                               │                               │
                       ▼                               ▼                               ▼
            ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
            │  /chat (POST)        │     │  /embed (POST)       │     │  /health (GET)      │
            │  app/ai/chat.py      │     │  app/ai/embedding.py │     │  app/ai/health.py   │
            └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                       │                               │
                       ▼                               │
            ┌─────────────────────┐                   │
            │  ChatService        │                   │
            │  app/services/       │                   │
            │  chat_service.py    │                   │
            │                     │                   │
            │  - chat()           │                   │
            │  - stream()         │                   │
            └─────────────────────┘                   │
                       │                               │
         ┌─────────────┴─────────────┐                 │
         │                           │                  │
         ▼                           ▼                  │
  ┌─────────────┐          ┌─────────────┐              │
  │ LLMProvider │          │ ToolExecutor│              │
  │ (Kilo.ai)   │          │             │              │
  └─────────────┘          └─────────────┘              │
                                    │                   │
                                    ▼                   │
                          ┌─────────────────┐          │
                          │ ToolRegistry    │          │
                          └─────────────────┘          │
                                    │                   │
           ┌────────────────────────┼───────────────────┘
           │                        │                      │
           ▼                        ▼                      ▼
  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
  │ SearchDocuments │    │ GetDocument    │    │ ListDocuments   │
  │ Tool            │    │ Tool           │    │ Tool            │
  └─────────────────┘    └─────────────────┘    └─────────────────┘
           │                        │                      │
           └────────────────────────┼──────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ Document        │
                          │ Repository      │
                          │ (InMemory)      │
                          └─────────────────┘
```

## Data Flow - Chat Request

```
User Question
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ChatService.chat()                          │
│ 1. Convert ChatRequest → messages format                         │
│ 2. Loop (max 5 rounds):                                          │
│    │                                                             │
│    ├──► LLMProvider.generate()                                   │
│    │        │                                                    │
│    │        ▼                                                    │
│    │   Check response for tool_calls                             │
│    │        │                                                    │
│    │   ┌────┴────┐                                               │
│    │   │         │                                               │
│    │  No        Yes                                              │
│    │   │         │                                               │
│    │   │         ▼                                               │
│    │   │   For each tool_call:                                   │
│    │   │       │                                                 │
│    │   │       ├──► ToolExecutor.execute()                       │
│    │   │       │         │                                       │
│    │   │       │         ├──► ToolRegistry.execute()             │
│    │   │       │         │         │                             │
│    │   │       │         │         ▼                             │
│    │   │       │         │   Validate arguments                  │
│    │   │       │         │         │                             │
│    │   │       │         │         ▼                             │
│    │   │       │         │   Execute tool                        │
│    │   │       │         │         │                             │
│    │   │       │         │         ▼                             │
│    │   │       │         └──► Return (result, ToolTrace)        │
│    │   │       │                                                    │
│    │   │       ▼                                                    │
│    │   │   Create tool_result message                             │
│    │   │       │                                                   │
│    │   └──► Append to messages                                    │
│    │                                                             │
│    └──► Return ChatResponse                                      │
└─────────────────────────────────────────────────────────────────┘
```

## RAG Pipeline Flow

```
Query ──► SemanticSearch ──► Context ──► Prompt ──► LLM ──► Answer
              │             Selector    Builder
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SemanticSearchService.search()                 │
│                                                                  │
│  1. query.strip()                                                │
│  2. embedding_provider.embed(query) → query_embedding            │
│  3. vector_store.search(query_embedding, top_k) → results       │
│  4. Filter by similarity_threshold                               │
│  5. Return SemanticSearchResponse                                │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RAGPromptBuilder.build_messages()               │
│                                                                  │
│  System: "You are a helpful knowledge-base assistant..."         │
│  User: "Context:\n[Source 1]\ndoc_id: ...\ncontent: ..."         │
│                                                                  │
│  - context truncated to max_context_chars (6000)                 │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LLMProvider.generate()                          │
│                                                                  │
│  - Uses Kilo.ai API                                              │
│  - Supports streaming                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Document Processing Flow

```
Document ──► Chunker ──► Embedding ──► VectorStore
            │           │
            ▼           ▼
      [Chunks]    [Vectors]
```

### Text Chunking (TextChunker)
- **Chunk size**: 500 characters (default)
- **Overlap**: 100 characters (default)
- **Step**: chunk_size - overlap = 400 characters

### Embedding (DocumentEmbeddingService)
- Uses EmbeddingProvider to generate vectors
- Each chunk gets its embedding stored in the chunk object

### Vector Storage (InMemoryVectorStore)
- Stores chunks with embeddings
- Search uses cosine similarity
- Results sorted by score (descending)

## Tool System Architecture

### BaseTool Abstract Class
```
BaseTool<T extends BaseModel>
├── name: str (abstract)
├── description: str (abstract)
├── input_model: Type[T] (abstract)
│
├── definition() → dict  # For LLM function calling
├── validate_arguments(dict) → T
└── execute(T) → Any  # Abstract
```

### Tool Registry Pattern
```
ToolRegistry
├── _tools: dict[str, BaseTool]
│
├── register(tool)
├── get(name) → BaseTool | None
├── execute(name, arguments) → Any
│   ├── Get tool by name
│   ├── Validate arguments
│   └── Execute tool
│
└── definitions() → list[dict]
```

### Tool Executor (with Tracing)
```
ToolExecutor
├── registry: ToolRegistry
│
├── definitions() → list[dict]
├── execute(name, arguments, tool_call_id)
│   ├── Generate trace_id (UUID)
│   ├── Record started_at
│   ├── Try:
│   │   ├── registry.execute(name, arguments)
│   │   └── Return (result, ToolTrace(success=True))
│   └── Catch ToolError:
│       └── Return (None, ToolTrace(success=False, error=...))
```

## Module Dependencies

```
main.py
├── logging_config.py
├── ai/chat.py
│   ├── services/chat_service.py
│   │   ├── providers/llm.py (ABC)
│   │   ├── tools/executor.py
│   │   └── tools/registry.py
│   │       └── tools/base.py
│   └── dependencies/chat.py
│       ├── config.py
│       ├── providers/kilo_llm.py
│       ├── documents/in_memory_repository.py
│       │   └── documents/repository.py (ABC)
│       └── tools/get_document.py, search_documents.py, list_documents.py
│
├── ai/embedding.py
│   └── services/embedding_service.py
│
└── ai/health.py
```

## Configuration

### Settings (app/config.py)
```python
class Settings(BaseSettings):
    kilo_api_key: str  # Required from .env
    kilo_model: str = "stepfun/step-3.7-flash:free"
```

### Environment Variables
```
KILO_API_KEY=your_api_key
KILO_MODEL=stepfun/step-3.7-flash:free
```

## Data Models

### Document Model
```python
class Document(BaseModel):
    document_id: str
    title: str
    content: str
    page: int | None = None
```

### DocumentChunk Model
```python
class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: dict
    embedding: list[float] | None
```

### SearchResult (Vector Store)
```python
@dataclass
class SearchResult:
    chunk: DocumentChunk
    score: float  # Cosine similarity
```

## Error Handling

### Tool Errors
```
ToolError (base)
├── ToolNotFoundError  # Tool not in registry
├── ToolValidationError  # Invalid arguments
└── ToolExecutionError  # Runtime error
```

### Chat Service Errors
```
ChatServiceError (base)
└── MaxToolRoundsExceededError  # > 5 tool calls
```

## Logging

### Log Format
```
%(asctime)s | %(levelname)s | %(name)s | %(message)s
2025-01-01 12:00:00 | INFO | app.tools.executor | Tool started | trace_id=... | tool=search_documents | arguments={...}
```

### Log Files
- Console (stdout)
- File: `logs/tools.log`

## Security Considerations

1. **Environment Variables**: API keys stored in `.env`, not in code
2. **Input Validation**: All inputs validated via Pydantic models
3. **Tool Arguments**: JSON validation before execution
4. **Max Tool Rounds**: Limited to 5 to prevent infinite loops

## Performance Considerations

1. **In-Memory Storage**: Fast access but limited by RAM
2. **Chunking**: Trade-off between context window and recall
3. **Vector Search**: O(n) for each search query
4. **Streaming**: Reduces perceived latency for LLM responses