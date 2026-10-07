# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/chat` | Chat with tool support |
| POST | `/chat/stream` | Streaming chat response |
| POST | `/embed` | Generate text embedding |

---

## Health Check

### GET `/health`

Health check endpoint to verify the service is running.

**Response**

```json
{
  "status": "ok"
}
```

**Example**
```bash
curl -X GET http://localhost:8000/health
```

---

## Chat

### POST `/chat`

Send a chat message and receive a response with optional tool execution.

**Request Body**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Tìm kiếm tài liệu về HR policy"
    }
  ],
  "temperature": 0.2,
  "max_tokens": 2000
}
```

**Parameters**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `messages` | `list[ChatMessage]` | Yes | - | List of chat messages |
| `temperature` | `float` | No | `0.2` | Sampling temperature (0-2) |
| `max_tokens` | `int` | No | `2000` | Maximum tokens in response |

**ChatMessage Object**

```json
{
  "role": "user | system | assistant | tool",
  "content": "string",
  "tool_calls": [...],  // optional, for assistant messages
  "tool_call_id": "string"  // optional, for tool messages
}
```

**Response**

```json
{
  "answer": "Dựa trên tài liệu HR Policy, nhân viên được nghỉ 12 ngày phép năm.",
  "model": "stepfun/step-3.7-flash:free"
}
```

**Example**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tìm kiếm tài liệu về HR policy"}
    ]
  }'
```

---

### POST `/chat/stream`

Send a chat message and receive a streaming response.

**Request Body**

Same as `/chat`

**Response**

Server-Sent Events (SSE) stream:

```
data: {"token": "Xin"}

data: {"token": " chào"}

data: {"token": " bạn"}

event: done
data: {}

```

**Headers**
- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `Connection: keep-alive`

**Example**
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Liệt kê các tài liệu có sẵn"}
    ]
  }'
```

---

## Embedding

### POST `/embed`

Generate an embedding vector for a text input.

**Request Body**

```json
{
  "text": "Nhân viên được nghỉ 12 ngày phép năm"
}
```

**Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | Yes | Text to embed |

**Response**

```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimenssion": 1536,
  "model": "text-embedding-ada-002"
}
```

**Note**: Currently returns a stub response (empty embedding).

**Example**
```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Nhân viên được nghỉ 12 ngày phép năm"}'
```

---

## Tool System

The chat endpoint supports function calling tools for document operations.

### Available Tools

#### 1. search_documents

Search documents in the knowledge base.

**Tool Definition**
```json
{
  "type": "function",
  "function": {
    "name": "search_documents",
    "description": "Search documents in the knowledge base.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Natural language query used to search documents"
        },
        "limit": {
          "type": "integer",
          "default": 5,
          "minimum": 1,
          "maximum": 20,
          "description": "Maximum number of documents to return"
        }
      },
      "required": ["query"]
    }
  }
}
```

**Example Tool Call**
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "search_documents",
    "arguments": "{\"query\": \"HR policy\", \"limit\": 5}"
  }
}
```

**Tool Response**
```json
{
  "query": "HR policy",
  "results": [
    {
      "document_id": "doc_001",
      "title": "HR Policy",
      "content": "Nhân viên được nghỉ 12 ngày phép năm.",
      "page": 12
    }
  ]
}
```

---

#### 2. get_document

Retrieve a document by its ID.

**Tool Definition**
```json
{
  "type": "function",
  "function": {
    "name": "get_document",
    "description": "Retrieve a document by its document ID.",
    "parameters": {
      "type": "object",
      "properties": {
        "document_id": {
          "type": "string",
          "minLength": 1,
          "description": "The unique ID of the document to retrieve"
        }
      },
      "required": ["document_id"]
    }
  }
}
```

**Example Tool Call**
```json
{
  "id": "call_def456",
  "type": "function",
  "function": {
    "name": "get_document",
    "arguments": "{\"document_id\": \"doc_001\"}"
  }
}
```

**Tool Response**
```json
{
  "found": true,
  "document": {
    "document_id": "doc_001",
    "title": "HR Policy",
    "content": "Nhân viên được nghỉ 12 ngày phép năm.",
    "page": 12
  }
}
```

---

#### 3. list_documents

List all available documents.

**Tool Definition**
```json
{
  "type": "function",
  "function": {
    "name": "list_documents",
    "description": "List documents currently available in the knowledge base.",
    "parameters": {
      "type": "object",
      "properties": {
        "limit": {
          "type": "integer",
          "default": 20,
          "minimum": 1,
          "maximum": 100,
          "description": "Maximum number of documents to return"
        }
      }
    }
  }
}
```

**Example Tool Call**
```json
{
  "id": "call_ghi789",
  "type": "function",
  "function": {
    "name": "list_documents",
    "arguments": "{\"limit\": 10}"
  }
}
```

**Tool Response**
```json
{
  "count": 3,
  "documents": [
    {"document_id": "doc_001", "title": "HR Policy", "page": 12},
    {"document_id": "doc_002", "title": "Company Handbook", "page": 8},
    {"document_id": "doc_003", "title": "Remote Work Policy", "page": 15}
  ]
}
```

---

## Error Responses

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "messages"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Tool Not Found (500)
```json
{
  "detail": "Tool 'unknown_tool' was not found"
}
```

### Tool Execution Error (500)
```json
{
  "detail": "Tool 'search_documents' execution failed"
}
```

---

## Rate Limits

No rate limits are currently enforced.

---

## Authentication

Currently no authentication is required.

---

## CORS

CORS configuration may vary. Check FastAPI app configuration.