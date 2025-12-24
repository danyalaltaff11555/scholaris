# Quickstart Guide

This guide provides step-by-step instructions to get Scholaris running on your local machine.

## Prerequisites

Before beginning, ensure you have the following installed:

- Python 3.10 or higher
- Docker (recommended) or local installations of Neo4j and Redis
- Git (for cloning the repository)

## Installation Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required Python packages including FastAPI, Neo4j drivers, Redis clients, and NLP libraries.

### Step 2: Database Setup

#### Option A: Using Docker (Recommended)

Start Neo4j:
```bash
docker run -d \
  --name scholaris-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Start Redis:
```bash
docker run -d \
  --name scholaris-redis \
  -p 6379:6379 \
  redis:latest
```

#### Option B: Local Installation

Refer to the [Deployment Guide](deployment.md) for detailed local installation instructions.

### Step 3: Configure Environment

Create environment configuration:
```bash
cp .env.example .env
```

Edit `.env` and configure the following required variables:

```bash
# LLM API Keys (at least one required)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

### Step 4: Initialize Database Schema

```bash
python scripts/setup_databases.py
```

Expected output:
```
Setting up Neo4j database...
Neo4j setup complete
Setting up Redis...
Redis setup complete
Database setup complete!
```

## Usage

### Document Ingestion

Ingest example documents:
```bash
python scripts/ingest_data.py --path examples/
```

Ingest your own documents:
```bash
python scripts/ingest_data.py --path /path/to/your/documents/
```

### Python Interface

```python
from scholaris import ScholarisChatbot

bot = ScholarisChatbot()

# Ingest a document
bot.ingest_document("document.pdf")

# Ask questions
response = bot.ask("What is the main topic of this document?")
print(response.answer)

# Clean up
bot.close()
```

### REST API Server

Start the API server:
```bash
python -m scholaris.api.main
```

The server will be available at:
- API endpoint: `http://localhost:8000`
- Interactive documentation: `http://localhost:8000/docs`

Query the API:
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

## Verification

Verify the installation is working correctly:

1. Check database connections:
```python
from scholaris.config import load_config
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.memory.redis_client import RedisClient

config = load_config()
neo4j = Neo4jClient(config)
redis = RedisClient(config)

print("Connections successful!")
neo4j.close()
```

2. Run tests:
```bash
pytest tests/
```

## Next Steps

- Review the [Architecture Overview](architecture.md) to understand system design
- Explore [Use Cases](usecases.md) for application examples
- Read the [Ingestion Guide](ingestion.md) for detailed document processing information
- Check the [API Documentation](api.md) for integration options
- Follow the [Deployment Guide](deployment.md) for production deployment

## Troubleshooting

**Database connection errors:**
- Verify Docker containers are running: `docker ps`
- Check port availability: `netstat -an | grep 7687` (Neo4j) and `netstat -an | grep 6379` (Redis)
- Confirm credentials in `.env` match database configuration

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.10+)

**API key errors:**
- Confirm API keys are set in `.env`
- Verify keys are valid and have available credits
- Check for extra whitespace in `.env` file

For additional help, refer to the [Deployment Guide](deployment.md) troubleshooting section.
