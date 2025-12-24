# System Architecture

## Overview

Scholaris is a knowledge graph-based question-answering system that combines symbolic reasoning with large language models to provide transparent, traceable answers. The architecture emphasizes modularity, type safety, and clean separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│         (REST API / Python SDK / CLI)                    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              ScholarisChatbot (Orchestrator)             │
│          Coordinates all subsystems and workflows        │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────┐  ┌──────▼─────┐  ┌────▼──────┐
│ Ingestion  │  │ Reasoning  │  │   Query   │
│  Pipeline  │  │   Engine   │  │ Processing│
└────────────┘  └────────────┘  └───────────┘
        │              │              │
┌───────▼────┐  ┌──────▼─────┐  ┌────▼──────┐
│Extraction  │  │    LLM     │  │   Graph   │
│  (NER/RE)  │  │   Client   │  │  Storage  │
└────────────┘  └────────────┘  └───────────┘
        │              │              │
┌───────▼────┐  ┌──────▼─────┐  ┌────▼──────┐
│Vector Store│  │   Memory   │  │  Cache    │
│ (ChromaDB) │  │  (Redis)   │  │ (Redis)   │
└────────────┘  └────────────┘  └───────────┘
```

## Core Components

### 1. Ingestion Pipeline

**Purpose:** Transform raw documents into structured knowledge representations.

**Components:**
- **Document Loader**: Extracts text from PDF, TXT, and Markdown files
- **Text Chunker**: Splits documents into semantically meaningful segments with overlap
- **Pipeline Orchestrator**: Coordinates the loading and chunking process

**Data Flow:**
```
Raw Document → Load Text → Chunk Text → Document Chunks → Extraction
```

**Key Features:**
- Supports multiple document formats
- Configurable chunk size and overlap
- Preserves document metadata
- Error handling for corrupted files

### 2. Extraction Module

**Purpose:** Identify entities and relationships from text using NLP techniques.

**Components:**
- **Entity Extractor**: Identifies named entities (concepts, authors, methods, etc.)
- **Relation Extractor**: Discovers relationships between entities
- **Entity Linker**: Resolves entity mentions to canonical forms

**Extraction Process:**
```
Text Chunk → NER → Entities → Relation Extraction → Relations → Deduplication → Canonical Entities
```

**Entity Types:**
- CONCEPT: Technical concepts and theories
- AUTHOR: Authors and researchers
- PAPER: Publications and papers
- METHOD: Methodologies and techniques
- DATASET: Datasets and corpora
- THEORY: Theoretical frameworks

**Relation Types:**
- DEFINES, USES, CITES, AUTHORED, PROPOSES, VALIDATES, CONTRADICTS, EXTENDS

### 3. Graph Module

**Purpose:** Store and query the knowledge graph using Neo4j.

**Components:**
- **Neo4j Client**: Manages database connections with connection pooling
- **Graph Builder**: Constructs the knowledge graph from extracted entities and relations
- **Graph Traversal**: Implements path finding and graph queries

**Graph Operations:**
```
Entities + Relations → Build Graph → Neo4j Storage → Query/Traversal → Graph Paths
```

**Key Features:**
- Parameterized queries for security
- Connection pooling for performance
- Index creation for fast lookups
- Shortest path algorithms
- Multi-hop traversal

### 4. Vector Store Module

**Purpose:** Enable semantic search over document chunks.

**Components:**
- **ChromaDB Client**: Manages vector storage and similarity search
- **Embedder**: Generates text embeddings using sentence transformers

**Vector Operations:**
```
Text → Embedding Model → Vector → ChromaDB → Similarity Search → Relevant Chunks
```

**Key Features:**
- Persistent storage
- In-memory embedding cache
- Batch processing support
- Configurable similarity metrics

### 5. Memory Module

**Purpose:** Manage conversation context and caching.

**Components:**
- **Redis Client**: Handles caching and session storage
- **Context Manager**: Tracks conversation history with token counting

**Context Management:**
```
User Message → Add to History → Count Tokens → Check Threshold → Summarize if needed → Store in Redis
```

**Key Features:**
- Automatic token counting
- Configurable summarization triggers
- TTL-based expiration
- Session isolation

### 6. Reasoning Module

**Purpose:** Analyze queries and generate chain-of-thought reasoning.

**Components:**
- **Query Analyzer**: Decomposes queries and identifies intent
- **Chain-of-Thought Engine**: Generates step-by-step reasoning traces
- **LangGraph Flow**: Orchestrates multi-step reasoning workflows

**Reasoning Process:**
```
Query → Analyze Intent → Decompose → Graph Search → CoT Steps → Verify Consistency → Response
```

**Query Intent Types:**
- FACTUAL: Direct fact retrieval
- COMPARATIVE: Comparing entities or concepts
- CAUSAL: Understanding cause-effect relationships
- PROCEDURAL: Step-by-step processes
- EXPLORATORY: Open-ended exploration

### 7. LLM Module

**Purpose:** Interface with large language models for text generation.

**Components:**
- **LLM Client**: Unified interface for Anthropic Claude and OpenAI GPT-4
- **Prompt Manager**: Loads and formats prompt templates from YAML

**LLM Integration:**
```
Prompt Template + Context → Format → LLM API → Generated Text → Response
```

**Key Features:**
- Multi-provider support (Anthropic, OpenAI)
- Automatic retry with exponential backoff
- Configurable temperature and token limits
- Prompt versioning

### 8. Explainability Module

**Purpose:** Format reasoning traces for human understanding.

**Components:**
- **Reasoning Formatter**: Converts reasoning steps to readable text
- **Graph Visualizer**: Generates graph path visualizations

**Output Formats:**
- Markdown-formatted reasoning traces
- Mermaid diagram syntax for graph paths
- Source citations with confidence scores

### 9. API Module

**Purpose:** Expose functionality via REST API.

**Components:**
- **FastAPI Application**: Main API server with CORS support
- **Route Handlers**: Endpoint implementations for query, ingest, and session management

**API Endpoints:**
- `POST /api/v1/query`: Process questions
- `POST /api/v1/ingest`: Ingest documents
- `DELETE /api/v1/session/{id}`: Clear sessions
- `GET /api/v1/health`: Health check
- `GET /api/v1/stats`: System statistics

## Data Flow

### Document Ingestion Flow

```
1. User submits document
2. Loader extracts text
3. Chunker splits into segments
4. Entity Extractor identifies entities
5. Relation Extractor finds relationships
6. Entity Linker deduplicates
7. Graph Builder adds to Neo4j
8. Embedder generates vectors
9. ChromaDB stores embeddings
```

### Query Processing Flow

```
1. User submits query
2. Query Analyzer identifies intent and entities
3. Graph Traversal searches for relevant nodes
4. Context Manager retrieves conversation history
5. CoT Engine generates reasoning steps
6. LLM Client generates answer
7. Formatter creates readable response
8. Context Manager stores interaction
9. Response returned to user
```

## Technology Stack

### Core Technologies
- **Python 3.10+**: Primary programming language
- **FastAPI**: REST API framework
- **Pydantic**: Data validation and settings management

### Databases
- **Neo4j**: Graph database for knowledge storage
- **Redis**: Cache and session management
- **ChromaDB**: Vector database for semantic search

### NLP and ML
- **Sentence Transformers**: Text embedding generation
- **spaCy**: Named entity recognition (placeholder)
- **Anthropic Claude / OpenAI GPT-4**: Large language models

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Static type checking
- **ruff**: Linting

## Design Principles

### 1. Modularity

Each component has a single, well-defined responsibility. Components communicate through clear interfaces defined by Pydantic models.

### 2. Type Safety

Extensive use of Python type hints and Pydantic models ensures type safety throughout the codebase. All data structures are validated at runtime.

### 3. Configuration Management

Centralized configuration using Pydantic-settings with environment variable support. All settings are validated at startup to fail fast.

### 4. Error Handling

Custom exception classes provide context for errors. All external calls (database, API) include retry logic and proper error propagation.

### 5. Logging

Structured logging with key-value pairs enables better log analysis and debugging. All components use a consistent logging interface.

### 6. Testability

Pure functions where possible, dependency injection for external services, and clear separation of concerns enable comprehensive testing.

## Scalability Considerations

### Horizontal Scaling

- **Stateless API**: Multiple API instances can run behind a load balancer
- **Shared State**: Redis and Neo4j provide shared state across instances
- **Async Processing**: Background job queues for document ingestion

### Performance Optimization

- **Connection Pooling**: Neo4j and Redis use connection pools
- **Caching**: Redis caches embeddings and query results
- **Batch Processing**: Entities and embeddings processed in batches
- **Index Optimization**: Neo4j indexes on frequently queried properties

### Resource Management

- **Configurable Limits**: Max tokens, max hops, batch sizes
- **TTL-based Expiration**: Automatic cleanup of old sessions
- **Graceful Degradation**: Fallback mechanisms for service failures

## Security Considerations

### Data Protection

- **Parameterized Queries**: Prevents injection attacks
- **Input Validation**: Pydantic models validate all inputs
- **Environment Variables**: Sensitive credentials stored securely

### API Security

- **CORS Configuration**: Configurable cross-origin policies
- **Rate Limiting**: Can be added via middleware
- **Authentication**: Extensible for OAuth2 or API keys

## Monitoring and Observability

### Logging

- Structured logs with consistent format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracking

### Metrics

- Query latency
- Document processing time
- Database connection pool status
- Cache hit rates

### Health Checks

- Database connectivity
- API endpoint availability
- System resource usage

## Future Enhancements

### Planned Features

- Advanced entity linking with external knowledge bases
- Multi-modal support (images, tables)
- Distributed processing for large document collections
- Real-time graph updates
- Advanced visualization tools

### Scalability Improvements

- Kubernetes deployment support
- Distributed caching with Redis Cluster
- Neo4j clustering for high availability
- Message queue integration for async processing

## References

- [Deployment Guide](deployment.md) - Production deployment instructions
- [API Documentation](api.md) - REST API reference
- [Use Cases](usecases.md) - Application examples
- [Ingestion Guide](ingestion.md) - Document processing details
