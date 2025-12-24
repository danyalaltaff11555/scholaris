# Scholaris - Knowledge Graph QA Chatbot with Chain-of-Thought Reasoning

> *From Latin "scholaris" - relating to schools and learning. A reasoning-powered chatbot that constructs explicit knowledge graphs from academic domains and uses chain-of-thought logic to answer questions with transparent, traceable explanations.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.14+-018bff.svg)](https://neo4j.com/)
[![Redis](https://img.shields.io/badge/Redis-5.0+-dc382d.svg)](https://redis.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

## Overview

**Scholaris** is an advanced question-answering system that transcends traditional RAG (Retrieval-Augmented Generation) by combining:

- **Structured Knowledge Graphs**: Symbolic representation of entities and relationships using Neo4j
- **Chain-of-Thought Reasoning**: Step-by-step logical inference paths
- **Explainable AI**: Transparent reasoning traces with graph path visualization
- **Context Management**: Redis-based caching with intelligent summarization
- **Hallucination Reduction**: Graph-grounded responses backed by verified relationships

## Quick Start

### Prerequisites

- Python 3.10+
- Neo4j (Docker or local installation)
- Redis (Docker or local installation)

### Installation

```bash
# Clone repository
git clone https://github.com/danyalaltaff11555/scholaris.git
cd scholaris

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys and database URLs

# Initialize databases
python scripts/setup_databases.py
```

### Basic Usage

```python
from scholaris import ScholarisChatbot

# Initialize chatbot
bot = ScholarisChatbot()

# Ingest documents
bot.ingest_document("./papers/research_paper.pdf")

# Ask questions
response = bot.ask("How do transformers improve upon RNN models?")

print(response.answer)
print(response.reasoning_trace)
print(response.sources)
```

### Run API Server

```bash
python -m scholaris.api.main

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 📚 Features

### 1. **Knowledge Graph Construction**
- Automatic entity and relation extraction from documents
- Neo4j-based graph storage with efficient indexing
- Support for PDF, TXT, and Markdown files

### 2. **Chain-of-Thought Reasoning**
- Step-by-step reasoning traces
- Graph-grounded inference
- Confidence scoring for each step

### 3. **Explainable Answers**
- Transparent reasoning process
- Source citations with document references
- Graph path visualization

### 4. **Context Management**
- Redis-based conversation memory
- Automatic summarization at token limits
- Session persistence

## Architecture

```
User Query → Query Analysis → Graph Traversal → CoT Reasoning → Response Synthesis
                ↓                    ↓                ↓
            Redis Cache        Neo4j Graph      LLM (Claude/GPT-4)
```

## Documentation

Comprehensive guides for deployment, usage, and contribution:

- **[Deployment Guide](docs/deployment.md)** - Complete setup instructions for all deployment scenarios
  - Database configuration (Neo4j, Redis, ChromaDB)
  - Docker and local installation options
  - Production deployment with Nginx and systemd
  - Troubleshooting and performance optimization

- **[Ingestion Guide](docs/ingestion.md)** - Detailed document processing workflow
  - Supported formats and preparation
  - Step-by-step ingestion process
  - Command-line and programmatic usage
  - Best practices and optimization

- **[Use Cases](docs/usecases.md)** - Real-world application examples
  - Academic research and literature review
  - Corporate knowledge management
  - Legal document analysis
  - Medical literature review
  - Integration patterns and code examples

- **[Architecture Overview](docs/architecture.md)** - System design and components

- **[API Documentation](docs/api.md)** - REST API reference and examples

- **[Contributing Guide](CONTRIBUTING.md)** - Development workflow and coding standards


## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scholaris

# Run specific test file
pytest tests/test_reasoning.py
```

## 🛠️ Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Format code
black src/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Performance

Target benchmarks:
- **Query Latency**: < 3s (time to first token)
- **Accuracy**: > 85% (vs ground truth)
- **Hallucination Rate**: < 5%

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

**Built with 🧠 for researchers and learners.**
