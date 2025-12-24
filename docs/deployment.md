# Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Application Configuration](#application-configuration)
4. [Installation Methods](#installation-methods)
5. [Production Deployment](#production-deployment)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Python 3.10 or higher
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space
- Docker (optional, for containerized databases)

### Required Services

1. **Neo4j Database** (Version 5.14+)
2. **Redis Cache** (Version 5.0+)
3. **LLM API Access** (Anthropic Claude or OpenAI GPT-4)

## Database Setup

### Option 1: Docker Deployment (Recommended)

#### Neo4j Setup

```bash
# Pull Neo4j image
docker pull neo4j:latest

# Run Neo4j container
docker run -d \
  --name scholaris-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_secure_password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  neo4j:latest

# Verify Neo4j is running
docker logs scholaris-neo4j
```

Access Neo4j Browser at `http://localhost:7474` and login with credentials.

#### Redis Setup

```bash
# Pull Redis image
docker pull redis:latest

# Run Redis container
docker run -d \
  --name scholaris-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:latest redis-server --appendonly yes

# Verify Redis is running
docker exec -it scholaris-redis redis-cli ping
# Expected output: PONG
```

### Option 2: Local Installation

#### Neo4j Local Installation

**Windows:**
```bash
# Download from https://neo4j.com/download/
# Install and configure through Neo4j Desktop
# Set database name: scholaris
# Set password and note it for configuration
```

**Linux/Mac:**
```bash
# Install Neo4j
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j

# Start Neo4j
sudo systemctl start neo4j
sudo systemctl enable neo4j

# Set initial password
cypher-shell -u neo4j -p neo4j
# Follow prompts to set new password
```

#### Redis Local Installation

**Windows:**
```bash
# Download from https://github.com/microsoftarchive/redis/releases
# Install and start Redis service
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Mac:**
```bash
brew install redis
brew services start redis
```

### Option 3: Cloud Services

#### Neo4j AuraDB (Managed Cloud)

1. Visit https://neo4j.com/cloud/aura/
2. Create free account
3. Create new database instance
4. Note connection URI, username, and password
5. Use URI format: `neo4j+s://xxxxx.databases.neo4j.io`

#### Redis Cloud

1. Visit https://redis.com/try-free/
2. Create free account
3. Create new database
4. Note connection string
5. Use format: `redis://default:password@host:port`

## Application Configuration

### Step 1: Clone Repository

```bash
git clone https://github.com/danyalaltaff11555/scholaris.git
cd scholaris
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# LLM API Keys (choose one or both)
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=scholaris

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Step 5: Initialize Database Schema

```bash
# Run database setup script
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

## Installation Methods

### Method 1: Standard Installation

```bash
# Install package in development mode
pip install -e .

# Verify installation
python -c "from scholaris import ScholarisChatbot; print('Installation successful')"
```

### Method 2: Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
    volumes:
      - neo4j_data:/data

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  scholaris:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - neo4j
      - redis
    environment:
      NEO4J_URI: bolt://neo4j:7687
      REDIS_URL: redis://redis:6379

volumes:
  neo4j_data:
  redis_data:
```

Run with:
```bash
docker-compose up -d
```

## Production Deployment

### Performance Optimization

#### Neo4j Configuration

Edit `neo4j.conf`:
```
dbms.memory.heap.initial_size=2g
dbms.memory.heap.max_size=4g
dbms.memory.pagecache.size=2g
dbms.connector.bolt.thread_pool_max_size=400
```

#### Redis Configuration

Edit `redis.conf`:
```
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### API Server Deployment

#### Using Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn scholaris.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

#### Using systemd Service (Linux)

Create `/etc/systemd/system/scholaris.service`:

```ini
[Unit]
Description=Scholaris API Service
After=network.target

[Service]
Type=notify
User=scholaris
Group=scholaris
WorkingDirectory=/opt/scholaris
Environment="PATH=/opt/scholaris/venv/bin"
ExecStart=/opt/scholaris/venv/bin/gunicorn scholaris.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable scholaris
sudo systemctl start scholaris
sudo systemctl status scholaris
```

#### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/scholaris`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/scholaris /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Verification

### Test Database Connections

```python
from scholaris.config import load_config
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.memory.redis_client import RedisClient

config = load_config()

# Test Neo4j
neo4j = Neo4jClient(config)
print("Neo4j connected successfully")
neo4j.close()

# Test Redis
redis = RedisClient(config)
redis.client.ping()
print("Redis connected successfully")
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","service":"scholaris"}
```

### Run Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scholaris --cov-report=html
```

## Troubleshooting

### Common Issues

#### Neo4j Connection Failed

**Problem:** `GraphConnectionError: Failed to connect to Neo4j`

**Solutions:**
1. Verify Neo4j is running: `docker ps` or `systemctl status neo4j`
2. Check credentials in `.env` match Neo4j configuration
3. Ensure port 7687 is not blocked by firewall
4. Test connection: `cypher-shell -a bolt://localhost:7687 -u neo4j -p password`

#### Redis Connection Failed

**Problem:** `redis.ConnectionError`

**Solutions:**
1. Verify Redis is running: `docker ps` or `systemctl status redis`
2. Test connection: `redis-cli ping`
3. Check REDIS_URL in `.env`
4. Ensure port 6379 is accessible

#### LLM API Errors

**Problem:** `ValueError: Anthropic API key not configured`

**Solutions:**
1. Verify API key is set in `.env`
2. Check API key is valid and has credits
3. Test API key directly with provider's CLI
4. Ensure no extra spaces in `.env` file

#### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'scholaris'`

**Solutions:**
1. Activate virtual environment
2. Install package: `pip install -e .`
3. Verify Python version: `python --version` (should be 3.10+)

#### Memory Issues

**Problem:** Out of memory errors during ingestion

**Solutions:**
1. Reduce batch size in `config.yaml`: `extraction.batch_size: 16`
2. Process documents one at a time
3. Increase system RAM or use cloud instance
4. Enable swap space on Linux

### Logging and Debugging

Enable debug logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
```

View logs:
```bash
# For systemd service
sudo journalctl -u scholaris -f

# For Docker
docker logs -f scholaris
```

### Performance Monitoring

Monitor Neo4j:
```bash
# Access Neo4j Browser
http://localhost:7474

# Run query to check node count
MATCH (n) RETURN count(n)
```

Monitor Redis:
```bash
redis-cli INFO memory
redis-cli INFO stats
```

## Security Considerations

### Production Checklist

- [ ] Change default database passwords
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable authentication on Redis
- [ ] Use API rate limiting
- [ ] Regular security updates

### Backup Strategy

**Neo4j Backup:**
```bash
# Create backup
docker exec scholaris-neo4j neo4j-admin dump --database=scholaris --to=/backups/scholaris.dump

# Restore backup
docker exec scholaris-neo4j neo4j-admin load --from=/backups/scholaris.dump --database=scholaris
```

**Redis Backup:**
```bash
# Redis automatically creates dump.rdb
# Copy from container
docker cp scholaris-redis:/data/dump.rdb ./backup/
```

## Next Steps

After successful deployment:

1. Review [Use Cases](usecases.md) for application examples
2. Read [API Documentation](api.md) for integration
3. Check [Architecture](architecture.md) for system understanding
4. See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
