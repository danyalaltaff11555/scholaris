# Ingestion Guide

## Table of Contents

1. [Overview](#overview)
2. [Document Formats](#document-formats)
3. [Ingestion Process](#ingestion-process)
4. [Command Line Usage](#command-line-usage)
5. [Programmatic Usage](#programmatic-usage)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

The ingestion pipeline processes documents through several stages:

1. **Loading:** Extract text from various file formats
2. **Chunking:** Split text into manageable segments
3. **Extraction:** Identify entities and relationships
4. **Graph Building:** Store in Neo4j knowledge graph

## Document Formats

### Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based PDFs (not scanned images) |
| Plain Text | `.txt` | UTF-8 encoding recommended |
| Markdown | `.md`, `.markdown` | Preserves structure |

### Format-Specific Considerations

**PDF Files:**
- Text must be selectable (not image-based)
- Complex layouts may affect extraction quality
- Multi-column documents are supported
- Embedded images are ignored

**Text Files:**
- Must be UTF-8 encoded
- Line breaks are preserved
- No special formatting

**Markdown Files:**
- Headers and structure are maintained
- Code blocks are treated as text
- Links are preserved in metadata

## Ingestion Process

### Stage 1: Document Loading

The loader extracts raw text from files:

```python
from scholaris.ingestion.loader import load_document

# Load a single document
document_id, content = load_document("paper.pdf")

print(f"Document ID: {document_id}")
print(f"Content length: {len(content)} characters")
```

**What happens:**
- File is validated and opened
- Text is extracted page by page (PDF) or as whole (TXT/MD)
- Unique document ID is generated
- Content is returned as string

### Stage 2: Text Chunking

Text is split into overlapping chunks:

```python
from scholaris.ingestion.chunker import chunk_text

chunks = chunk_text(
    text=content,
    document_id=document_id,
    chunk_size=1000,      # Characters per chunk
    overlap=200           # Overlap between chunks
)

print(f"Created {len(chunks)} chunks")
for chunk in chunks[:3]:
    print(f"Chunk {chunk.id}: {len(chunk.text)} chars")
```

**Parameters:**
- `chunk_size`: Target size in characters (default: 1000)
- `overlap`: Overlap between chunks (default: 200)

**Why chunking matters:**
- Enables processing of large documents
- Maintains context across boundaries
- Optimizes for LLM context windows

### Stage 3: Entity Extraction

Entities are identified in each chunk:

```python
from scholaris.extraction.entities import EntityExtractor
from scholaris.config import load_config

config = load_config()
extractor = EntityExtractor(config)

entities = extractor.extract_entities(chunk.text)

for entity in entities:
    print(f"{entity.type}: {entity.text} (confidence: {entity.confidence})")
```

**Entity Types:**
- `CONCEPT`: Technical concepts, theories
- `AUTHOR`: Authors, researchers
- `PAPER`: Paper titles, publications
- `METHOD`: Methodologies, techniques
- `DATASET`: Datasets, corpora
- `THEORY`: Theoretical frameworks

### Stage 4: Relation Extraction

Relationships between entities are identified:

```python
from scholaris.extraction.relations import RelationExtractor

rel_extractor = RelationExtractor(config)
relations = rel_extractor.extract_relations(chunk.text, entities)

for relation in relations:
    print(f"{relation.source_id} --{relation.type}--> {relation.target_id}")
```

**Relation Types:**
- `DEFINES`: Entity defines another
- `USES`: Entity uses another
- `CITES`: Paper cites another
- `AUTHORED`: Author wrote paper
- `PROPOSES`: Proposes theory/method
- `VALIDATES`: Validates with data
- `CONTRADICTS`: Contradicts claim
- `EXTENDS`: Extends previous work

### Stage 5: Graph Construction

Entities and relations are stored in Neo4j:

```python
from scholaris.graph.builder import GraphBuilder
from scholaris.graph.neo4j_client import Neo4jClient

neo4j = Neo4jClient(config)
builder = GraphBuilder(config, neo4j)

# Add to graph
builder.build_graph(entities, relations)

print("Graph updated successfully")
neo4j.close()
```

## Command Line Usage

### Single File Ingestion

```bash
python scripts/ingest_data.py --path documents/research_paper.pdf
```

**Output:**
```
Ingesting file: documents/research_paper.pdf
Ingested 45 chunks, 120 entities, 85 relations
Ingestion complete!
```

### Directory Ingestion

```bash
# Ingest all supported files in directory
python scripts/ingest_data.py --path documents/papers/

# Recursive ingestion
python scripts/ingest_data.py --path documents/ --recursive
```

**Progress Output:**
```
Ingesting file: documents/papers/paper1.pdf
Ingested 32 chunks, 95 entities, 67 relations
Ingesting file: documents/papers/paper2.pdf
Ingested 28 chunks, 78 entities, 54 relations
...
Ingestion complete!
```

### Advanced Options

```bash
# Custom chunk size
python scripts/ingest_data.py \
  --path documents/ \
  --chunk-size 1500 \
  --overlap 300

# Specific file types only
python scripts/ingest_data.py \
  --path documents/ \
  --extensions pdf md
```

## Programmatic Usage

### Basic Ingestion

```python
from scholaris import ScholarisChatbot

bot = ScholarisChatbot()

# Ingest single document
result = bot.ingest_document("paper.pdf")

print(f"Document ID: {result['document_id']}")
print(f"Chunks: {result['chunks']}")
print(f"Entities: {result['entities']}")
print(f"Relations: {result['relations']}")
```

### Batch Ingestion

```python
import os
from pathlib import Path

bot = ScholarisChatbot()

# Get all PDF files
documents = Path("documents/").glob("**/*.pdf")

results = []
for doc in documents:
    try:
        result = bot.ingest_document(str(doc))
        results.append(result)
        print(f"Processed: {doc.name}")
    except Exception as e:
        print(f"Failed: {doc.name} - {e}")

# Summary
total_entities = sum(r['entities'] for r in results)
total_relations = sum(r['relations'] for r in results)

print(f"\nTotal: {len(results)} documents")
print(f"Total entities: {total_entities}")
print(f"Total relations: {total_relations}")
```

### Custom Pipeline

```python
from scholaris.ingestion.pipeline import IngestionPipeline
from scholaris.extraction.entities import EntityExtractor
from scholaris.extraction.relations import RelationExtractor
from scholaris.graph.builder import GraphBuilder
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.config import load_config

config = load_config()

# Initialize components
pipeline = IngestionPipeline(chunk_size=1500, overlap=300)
entity_extractor = EntityExtractor(config)
relation_extractor = RelationExtractor(config)
neo4j = Neo4jClient(config)
graph_builder = GraphBuilder(config, neo4j)

# Process document
document_id, chunks = pipeline.process_document("paper.pdf")

all_entities = []
all_relations = []

for chunk in chunks:
    # Extract entities
    entities = entity_extractor.extract_entities(chunk.text)
    all_entities.extend(entities)
    
    # Extract relations
    relations = relation_extractor.extract_relations(chunk.text, entities)
    all_relations.extend(relations)

# Deduplicate
unique_entities = entity_extractor.deduplicate_entities(all_entities)

# Build graph
graph_builder.build_graph(unique_entities, all_relations)

print(f"Processed: {len(chunks)} chunks")
print(f"Extracted: {len(unique_entities)} unique entities")
print(f"Extracted: {len(all_relations)} relations")

neo4j.close()
```

### Monitoring Progress

```python
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)

documents = list(Path("documents/").glob("*.pdf"))

for doc in tqdm(documents, desc="Ingesting documents"):
    try:
        result = bot.ingest_document(str(doc))
        tqdm.write(f"✓ {doc.name}: {result['entities']} entities")
    except Exception as e:
        tqdm.write(f"✗ {doc.name}: {str(e)}")
```

## Best Practices

### Document Preparation

1. **Clean Documents:**
   - Remove unnecessary headers/footers
   - Ensure text is selectable in PDFs
   - Use consistent formatting

2. **Organize by Topic:**
   - Group related documents in directories
   - Use descriptive filenames
   - Maintain consistent naming conventions

3. **Size Considerations:**
   - Individual files: < 50MB recommended
   - Total corpus: Monitor disk space and memory

### Optimization

1. **Chunk Size Selection:**
   ```python
   # For technical documents with dense information
   chunk_size = 800
   overlap = 150
   
   # For narrative documents
   chunk_size = 1500
   overlap = 300
   ```

2. **Batch Processing:**
   ```python
   # Process in batches to manage memory
   batch_size = 10
   documents = list(Path("docs/").glob("*.pdf"))
   
   for i in range(0, len(documents), batch_size):
       batch = documents[i:i+batch_size]
       for doc in batch:
           bot.ingest_document(str(doc))
       
       # Optional: Clear cache between batches
       import gc
       gc.collect()
   ```

3. **Parallel Processing:**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def ingest_file(filepath):
       bot = ScholarisChatbot()
       return bot.ingest_document(filepath)
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = list(executor.map(ingest_file, documents))
   ```

### Quality Control

1. **Verify Extraction:**
   ```python
   result = bot.ingest_document("paper.pdf")
   
   # Check entity count
   if result['entities'] < 10:
       print("Warning: Low entity count, check document quality")
   
   # Check relation count
   if result['relations'] < 5:
       print("Warning: Few relations extracted")
   ```

2. **Sample Inspection:**
   ```python
   # Inspect first few entities
   entities = entity_extractor.extract_entities(chunks[0].text)
   for entity in entities[:10]:
       print(f"{entity.type}: {entity.text}")
   ```

## Troubleshooting

### Common Issues

**Issue: "No text extracted from PDF"**

Solution:
```python
# Check if PDF is text-based
import PyPDF2

with open("document.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    text = reader.pages[0].extract_text()
    
    if not text.strip():
        print("PDF appears to be image-based, use OCR")
```

**Issue: "Memory error during ingestion"**

Solution:
```python
# Reduce chunk size
pipeline = IngestionPipeline(chunk_size=500, overlap=100)

# Process one document at a time
# Clear cache between documents
```

**Issue: "Few entities extracted"**

Solution:
```python
# Lower confidence threshold
config.extraction.entity_confidence_threshold = 0.5

# Check document content
print(chunks[0].text[:500])  # Inspect first chunk
```

**Issue: "Duplicate entities in graph"**

Solution:
```python
# Ensure deduplication
unique_entities = entity_extractor.deduplicate_entities(all_entities)

# Use entity linker
from scholaris.extraction.linker import EntityLinker
linker = EntityLinker()
linker.link_entities(unique_entities)
```

### Performance Issues

**Slow ingestion:**

1. Check database connection latency
2. Reduce batch size
3. Enable connection pooling
4. Use local databases instead of cloud

**High memory usage:**

1. Process documents sequentially
2. Reduce chunk size
3. Clear caches periodically
4. Use streaming for large files

### Validation

```python
# Verify graph was updated
from scholaris.graph.neo4j_client import Neo4jClient

neo4j = Neo4jClient(config)

# Count nodes
result = neo4j.execute_query("MATCH (n) RETURN count(n) as count")
print(f"Total nodes: {result[0]['count']}")

# Count relationships
result = neo4j.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
print(f"Total relationships: {result[0]['count']}")

neo4j.close()
```

## Next Steps

After successful ingestion:

1. Query the knowledge graph using the chatbot
2. Visualize the graph in Neo4j Browser
3. Review [Use Cases](usecases.md) for application examples
4. Check [API Documentation](api.md) for integration options
