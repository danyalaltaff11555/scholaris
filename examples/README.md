# Scholaris Examples

This directory contains example documents to help you get started with Scholaris and test the system before adding your own data.

## Example Documents

### example_transformers.md
Comprehensive overview of Transformer architecture covering:
- Self-attention mechanisms and multi-head attention
- Architecture components and design principles
- Advantages over RNNs and CNNs
- Variants (BERT, GPT, T5, Transformer-XL)
- Applications in NLP and beyond
- Implementation considerations

### example_ml_basics.md
Machine learning fundamentals including:
- Core concepts and terminology
- Types of learning (supervised, unsupervised, reinforcement)
- Common algorithms (decision trees, neural networks, SVMs)
- Model evaluation and validation
- Feature engineering and preprocessing
- Real-world applications

## Quick Start

### 1. Setup Databases

Make sure Neo4j and Redis are running:

```bash
# Using Docker
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
docker run -d --name redis -p 6379:6379 redis:latest

# Initialize database schema
python scripts/setup_databases.py
```

### 2. Ingest Example Documents

```bash
# Ingest all examples
python scripts/ingest_data.py --path examples/

# Or ingest individually
python scripts/ingest_data.py --path examples/example_transformers.md
python scripts/ingest_data.py --path examples/example_ml_basics.md
```

Expected output:
```
Ingesting file: examples/example_transformers.md
Ingested 45 chunks, 120 entities, 85 relations
Ingesting file: examples/example_ml_basics.md
Ingested 38 chunks, 95 entities, 67 relations
Ingestion complete!
```

### 3. Query the System

#### Using Python

```python
from scholaris import ScholarisChatbot

bot = ScholarisChatbot()

# Ask questions
response = bot.ask("What is a Transformer?")
print(response.answer)

# With reasoning trace
response = bot.ask("How does self-attention work?", include_reasoning=True)
print(response.answer)
for step in response.reasoning_trace:
    print(f"Step {step.step_number}: {step.description}")

bot.close()
```

#### Using API Server

Start the server:
```bash
python -m scholaris.api.main
```

The server will start at `http://localhost:8000`

Access interactive API docs at `http://localhost:8000/docs`

Query via curl:
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is a Transformer?",
    "include_reasoning": true
  }'
```

Query via Python requests:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "What are the types of machine learning?",
        "include_reasoning": True
    }
)

result = response.json()
print(result['answer'])
```

## Example Queries

Try these questions to explore the system:

### About Transformers
- "What is a Transformer?"
- "How does self-attention work in Transformers?"
- "What are the advantages of Transformers over RNNs?"
- "What is BERT and how does it differ from GPT?"
- "What are the key components of Transformer architecture?"

### About Machine Learning
- "What are the types of machine learning?"
- "What is supervised learning?"
- "How does cross-validation work?"
- "What is overfitting and how do you prevent it?"
- "What are ensemble methods?"

### Comparative Questions
- "How do Transformers compare to RNNs?"
- "What is the difference between supervised and unsupervised learning?"
- "How does BERT differ from GPT?"

### Multi-hop Questions
- "How do attention mechanisms in Transformers relate to neural network architectures in machine learning?"
- "What machine learning techniques are used in Transformer training?"

## Verifying Ingestion

Check that data was ingested correctly:

### Using Neo4j Browser

1. Open `http://localhost:7474` in your browser
2. Login with credentials (neo4j/password)
3. Run queries:

```cypher
// Count total nodes
MATCH (n) RETURN count(n)

// View entity types
MATCH (n) RETURN DISTINCT labels(n), count(n)

// Search for specific entity
MATCH (n) WHERE toLower(n.text) CONTAINS 'transformer' RETURN n LIMIT 10

// View relationships
MATCH ()-[r]->() RETURN type(r), count(r)
```

### Using Python

```python
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.config import load_config

config = load_config()
client = Neo4jClient(config)

# Count nodes
result = client.execute_query("MATCH (n) RETURN count(n) as count")
print(f"Total nodes: {result[0]['count']}")

# Count relationships
result = client.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
print(f"Total relationships: {result[0]['count']}")

client.close()
```

## Troubleshooting

### No entities extracted
- Check that documents were ingested: `ls data/processed/`
- Verify Neo4j is running: `docker ps`
- Check logs for errors

### Empty responses
- Ensure documents are ingested before querying
- Verify LLM API keys are set in `.env`
- Check that Neo4j contains data (see verification above)

### Connection errors
- Verify Neo4j is running on port 7687
- Verify Redis is running on port 6379
- Check credentials in `.env` match database settings

## Next Steps

After testing with examples:

1. **Add Your Own Documents**: Place PDFs, TXT, or MD files in `data/raw/`
2. **Ingest Your Data**: Run `python scripts/ingest_data.py --path data/raw/`
3. **Explore Use Cases**: See [docs/usecases.md](../docs/usecases.md) for application ideas
4. **Deploy to Production**: Follow [docs/deployment.md](../docs/deployment.md)
5. **Integrate via API**: Check [docs/api.md](../docs/api.md) for integration patterns

## Performance Notes

- Initial ingestion may take 1-2 minutes for these examples
- Query response time: typically 2-5 seconds
- First query may be slower due to model loading
- Subsequent queries benefit from caching

## Additional Resources

- [Deployment Guide](../docs/deployment.md) - Production setup
- [Ingestion Guide](../docs/ingestion.md) - Detailed ingestion workflow
- [API Documentation](../docs/api.md) - REST API reference
- [Architecture Overview](../docs/architecture.md) - System design
