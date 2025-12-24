"""
Database setup script.

Initializes Neo4j schema and Redis configuration.
"""

from scholaris.config import load_config
from scholaris.graph.builder import GraphBuilder
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.memory.redis_client import RedisClient
from scholaris.utils.logging import setup_logging

logger = setup_logging("INFO")


def setup_neo4j(config):
    """Initialize Neo4j database with schema and indexes."""
    logger.info("Setting up Neo4j database...")

    client = Neo4jClient(config)
    builder = GraphBuilder(config, client)

    builder.create_indexes()

    logger.info("Neo4j setup complete")
    client.close()


def setup_redis(config):
    """Initialize Redis configuration."""
    logger.info("Setting up Redis...")

    client = RedisClient(config)
    client.client.ping()

    logger.info("Redis setup complete")


def main():
    """Main setup function."""
    config = load_config()

    logger.info("Starting database setup...")

    setup_neo4j(config)
    setup_redis(config)

    logger.info("Database setup complete!")


if __name__ == "__main__":
    main()
