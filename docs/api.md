# API Documentation

## Overview

Scholaris provides a RESTful API built with FastAPI for integrating knowledge graph question-answering capabilities into your applications. The API supports document ingestion, query processing, and session management.

## Base URL

```
http://localhost:8000/api/v1
```

For production deployments, replace `localhost:8000` with your deployed server address.

## Authentication

Currently, the API does not require authentication. For production deployments, implement authentication middleware as needed.

## Endpoints

### Health Check

Check API service status.

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "scholaris"
}
```

**Status Codes:**
- `200 OK`: Service is operational

---

### Query Processing

Submit a question and receive an answer with optional reasoning traces.

**Endpoint:** `POST /api/v1/query`

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "session_id": "optional-session-id",
  "max_hops": 3,
  "include_reasoning": true
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | The question to answer |
| `session_id` | string | No | Auto-generated | Session identifier for conversation context |
| `max_hops` | integer | No | 3 | Maximum graph traversal depth (1-10) |
| `include_reasoning` | boolean | No | true | Include chain-of-thought reasoning steps |

**Response:**
```json
{
  "query": "What is machine learning?",
  "answer": "Machine learning is a branch of artificial intelligence...",
  "reasoning_trace": [
    {
      "step_number": 1,
      "description": "Identify key concepts in the question",
      "action": "concept_extraction",
      "result": "Extracted concepts: machine learning, definition",
      "confidence": 0.9
    },
    {
      "step_number": 2,
      "description": "Search knowledge graph for relevant information",
      "action": "graph_query",
      "result": "Found 15 related entities",
      "confidence": 0.85
    }
  ],
  "sources": [],
  "confidence": 0.85,
  "timestamp": "2024-12-24T15:30:00"
}
```

**Status Codes:**
- `200 OK`: Query processed successfully
- `500 Internal Server Error`: Query processing failed

---

### Document Ingestion

Ingest a document into the knowledge graph.

**Endpoint:** `POST /api/v1/ingest`

**Request Body:**
```json
{
  "file_path": "/absolute/path/to/document.pdf"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to the document file |

**Response:**
```json
{
  "status": "success",
  "document_id": "abc123def456",
  "chunks": 45,
  "entities": 120
}
```

**Status Codes:**
- `200 OK`: Document ingested successfully
- `500 Internal Server Error`: Ingestion failed

---

### Session Management

Clear conversation history for a specific session.

**Endpoint:** `DELETE /api/v1/session/{session_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string | Session identifier to clear |

**Response:**
```json
{
  "status": "success",
  "message": "Session abc123 cleared"
}
```

**Status Codes:**
- `200 OK`: Session cleared successfully

---

### System Statistics

Retrieve system configuration and status information.

**Endpoint:** `GET /api/v1/stats`

**Response:**
```json
{
  "status": "operational",
  "provider": "anthropic",
  "model": "claude-sonnet-4"
}
```

**Status Codes:**
- `200 OK`: Statistics retrieved successfully

## Usage Examples

### Python Client

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Ingest a document
response = requests.post(
    f"{API_URL}/ingest",
    json={"file_path": "/path/to/document.pdf"}
)
print(response.json())

# Query with reasoning
response = requests.post(
    f"{API_URL}/query",
    json={
        "query": "What is the main contribution?",
        "include_reasoning": True
    }
)
result = response.json()
print(result['answer'])

# View reasoning steps
for step in result['reasoning_trace']:
    print(f"Step {step['step_number']}: {step['description']}")
```

### cURL Examples

Query:
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is a Transformer?",
    "include_reasoning": true
  }'
```

Ingest:
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf"}'
```

Clear session:
```bash
curl -X DELETE "http://localhost:8000/api/v1/session/abc123"
```

### JavaScript/TypeScript

```typescript
const API_URL = 'http://localhost:8000/api/v1';

async function query(question: string): Promise<any> {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: question,
      include_reasoning: true
    })
  });
  return response.json();
}

const result = await query('What is machine learning?');
console.log(result.answer);
```

## Interactive Documentation

FastAPI provides automatically generated interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- Explore all available endpoints
- View request/response schemas
- Test API calls directly in the browser
- Download OpenAPI specification

## Error Handling

All endpoints return standard HTTP status codes. Error responses include details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error scenarios:
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side processing error

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing rate limiting middleware to prevent abuse.

## Best Practices

1. **Session Management**: Use consistent session IDs for conversational context
2. **Error Handling**: Implement retry logic with exponential backoff
3. **Timeouts**: Set appropriate request timeouts (recommended: 60 seconds)
4. **Batch Processing**: For multiple documents, ingest sequentially to avoid overwhelming the system
5. **Monitoring**: Track response times and error rates in production

## Next Steps

- Review [Use Cases](usecases.md) for integration patterns
- Check [Deployment Guide](deployment.md) for production setup
- Explore [Architecture](architecture.md) for system understanding
