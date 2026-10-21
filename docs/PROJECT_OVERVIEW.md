# Project Overview - Knowledge Base

## Giới thiệu

**Knowledge Base** là một hệ thống RAG (Retrieval-Augmented Generation) được xây dựng bằng Python và FastAPI. Hệ thống cho phép người dùng tải lên tài liệu, tìm kiếm thông tin trong tài liệu bằng ngôn ngữ tự nhiên, và nhận câu trả lời từ LLM (Large Language Model) dựa trên ngữ cảnh từ tài liệu.

## Tính năng chính

### 1. Chat với ngữ cảnh (RAG)
- Người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên
- Hệ thống tìm kiếm các đoạn tài liệu liên quan
- LLM tạo câu trả lời dựa trên ngữ cảnh từ tài liệu
- Hỗ trợ streaming response

### 2. Quản lý tài liệu
- Lưu trữ tài liệu với metadata (title, page)
- Chia nhỏ tài liệu thành các chunks với overlap
- Tạo embedding vector cho mỗi chunk
- Lưu trữ vector trong bộ nhớ (in-memory vector store)

### 3. Semantic Search
- Tìm kiếm theo ngữ nghĩa sử dụng vector similarity
- Sử dụng cosine similarity để đo lường sự tương đồng
- Hỗ trợ similarity threshold để lọc kết quả

### 4. Tool Agent System
- Định nghĩa các tool dạng function calling
- Tool registry để quản lý các tool
- Tool executor với tracing và logging
- Các tool có sẵn: `search_documents`, `get_document`, `list_documents`

### 5. OCR (Optical Character Recognition)
- Nhận diện văn bản từ hình ảnh
- Hỗ trợ 3 nguồn hình ảnh:
  - **URL**: Hình ảnh từ internet (http/https)
  - **Base64**: Image bytes dạng Base64 data URL
  - **File ID**: File đã upload lên Files API
- Tích hợp với Meta AI API (muse-spark-1.3)
- Hỗ trợ nhiều ngôn ngữ (Vietnamese, English, Japanese, Korean, Chinese)
- Streaming response cho kết quả real-time
- OCR tool cho phép agent nhận diện text từ hình ảnh

## Công nghệ sử dụng

### Core
- **Python 3.12+**
- **FastAPI** - Web framework
- **Pydantic** - Data validation

### AI/ML
- **OpenAI-compatible API** - Kilo.ai là LLM provider mặc định
- **Embedding Models** - Text embedding cho semantic search

### Libraries
- `websockets` - WebSocket support
- `httptools` - HTTP parsing
- `h11` - HTTP/1.1
- `uvicorn` - ASGI server

## Cấu trúc project

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Settings và configuration
├── logging_config.py    # Logging setup
├── ai/                  # API routes
│   ├── chat.py          # Chat endpoint (streaming)
│   ├── embedding.py     # Embedding endpoint
│   ├── ocr.py           # OCR endpoint (image text recognition)
│   └── health.py        # Health check
├── models/              # Pydantic models
│   ├── chat.py          # Chat request/response
│   ├── embedding.py     # Embedding request/response
│   └── ocr.py           # OCR request/response
├── providers/           # AI providers
│   ├── llm.py           # Abstract LLM provider
│   ├── kilo_llm.py      # Kilo.ai implementation
│   ├── mock_llm.py      # Mock LLM provider
│   ├── embedding.py     # Abstract embedding provider
│   ├── fake_embedding.py # Mock embedding provider
│   └── ocr_provider.py  # OCR providers (Meta, Mock, Local)
├── services/            # Business logic
│   ├── chat_service.py  # Chat service với tool calling
│   ├── embedding_service.py # Embedding service
│   └── ocr_service.py   # OCR service
├── tools/               # Tool system
│   ├── base.py          # BaseTool abstract class
│   ├── registry.py      # ToolRegistry
│   ├── executor.py      # ToolExecutor với tracing
│   ├── tracing.py       # ToolTrace model
│   ├── errors.py        # Tool exceptions
│   ├── search_documents.py # Search tool
│   ├── get_document.py  # Get document tool
│   ├── list_documents.py # List documents tool
│   └── ocr_tool.py     # OCR tool
├── documents/           # Document management
│   ├── models.py        # Document model
│   ├── repository.py    # Abstract repository
│   ├── in_memory_repository.py # In-memory implementation
│   ├── chunker.py       # Text chunking
│   ├── chunks.py        # DocumentChunk model
│   └── embedding_service.py # Document embedding
├── vectorstores/        # Vector storage
│   ├── in_memory.py     # InMemoryVectorStore
│   └── similarity.py   # Cosine similarity
├── search/              # Search service
│   ├── models.py        # Search models
│   └── service.py       # SemanticSearchService
├── rag/                 # RAG pipeline
│   ├── models.py        # RAG response model
│   ├── prompt_builder.py # Prompt builder
│   ├── context_selector.py # Context selector
│   └── service.py       # RAG service
├── evaluation/          # Evaluation metrics
│   └── retrieval.py     # hit_@k, precision_@k, recall_@k
└── dependencies/        # FastAPI dependencies
    └── chat.py          # Chat service dependencies
```

## API Endpoints

### Health Check
```
GET /health
```
- Response: `{"status": "ok"}`

### Chat
```
POST /chat
```
- Request: `ChatRequest` với messages, temperature, max_tokens
- Response: `ChatResponse` với answer và model
- Hỗ trợ tool calling cho document operations

### Chat Streaming
```
POST /chat/stream
```
- Response: Server-Sent Events (SSE) stream
- Format: `data: {"token": "..."}\n\n`

### Embedding
```
POST /embed
```
- Request: `EmbeddingRequest` với text
- Response: `EmbeddingResponse` với embedding vector

### OCR
```
POST /ocr
```
- Request: `OCRRequest` với source_type và image data (url/base64/file_id)
- Response: `OCRResponse` với danh sách text được nhận diện

### OCR Streaming
```
POST /ocr/stream
```
- Response: Server-Sent Events (SSE) stream
- Format: `data: {"status": "text_found", "text": "...", "index": 0}\n\n`

### OCR Providers Info
```
GET /ocr/providers
```
- Response: Thông tin về các OCR providers được hỗ trợ

### OCR Health
```
GET /ocr/health
```
- Response: `{"status": "ok", "service": "ocr", "provider": "...", "model": "..."}`

## Sample Documents

Hệ thống có sẵn 3 sample documents:
1. **doc_001** - HR Policy (Nhân viên được nghỉ 12 ngày phép năm)
2. **doc_002** - Company Handbook (Nhân viên cần gửi đơn nghỉ phép)
3. **doc_003** - Remote Work Policy (Nhân viên có thể làm việc từ xa)

## Tool System

### Available Tools

#### 1. search_documents
- **Purpose**: Tìm kiếm tài liệu bằng ngôn ngữ tự nhiên
- **Input**: query (string), limit (int, default 5)
- **Returns**: Danh sách các tài liệu liên quan

#### 2. get_document
- **Purpose**: Lấy thông tin tài liệu theo ID
- **Input**: document_id (string)
- **Returns**: Thông tin tài liệu hoặc thông báo không tìm thấy

#### 3. list_documents
- **Purpose**: Liệt kê các tài liệu có sẵn
- **Input**: limit (int, default 20)
- **Returns**: Danh sách tài liệu với document_id, title, page

#### 4. ocr_image
- **Purpose**: Nhận diện văn bản từ hình ảnh
- **Input**: source_type (url/base64/file_id), url/base64_data/file_id, prompt (optional)
- **Returns**: Văn bản được nhận diện cùng với ngôn ngữ phát hiện

## Environment Variables

```bash
# Required
KILO_API_KEY=your_api_key_here

# Optional (with defaults)
KILO_MODEL=stepfun/step-3.7-flash:free

# OCR Configuration (optional)
META_AI_API_KEY=your_meta_api_key_here  # For MetaOCRProvider
OCR_MODEL=muse-spark-1.3  # Default OCR model
OCR_PROVIDER=mock  # mock, meta, or local
```

## Logging

Logs được ghi vào:
- Console (stdout)
- File: `logs/tools.log`

Format: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`

## Known Issues

1. **Typo in `app/services/embedding_service.py`**:
   - Line 5: `sefl` should be `self`
   - Line 5: `dimenssion` should be `dimension`

2. **Embedding service là stub**: Hiện tại chỉ trả về empty embedding, chưa implement thực sự

3. **Document repository là in-memory**: Dữ liệu sẽ mất khi restart server

## Future Improvements

1. Implement embedding service thực sự
2. Thêm persistent storage (SQLite, PostgreSQL)
3. Thêm vector database (Milvus, Qdrant, Chroma)
4. Thêm authentication/authorization
5. Thêm document upload API
6. Cải thiện chunking strategy
7. Thêm re-ranking cho search results