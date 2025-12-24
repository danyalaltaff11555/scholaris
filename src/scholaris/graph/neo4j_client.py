from typing import Any, Optional

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable

from scholaris.config import Config
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class GraphConnectionError(Exception):
    pass


class Neo4jClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.driver: Optional[Driver] = None
        self._connect()

    def _connect(self) -> None:
        try:
            self.driver = GraphDatabase.driver(
                self.config.neo4j.uri,
                auth=(self.config.neo4j.user, self.config.neo4j.password),
                max_connection_lifetime=self.config.neo4j.max_connection_lifetime,
                max_connection_pool_size=self.config.neo4j.max_connection_pool_size,
            )

            self.driver.verify_connectivity()
            logger.info("neo4j_connected", uri=self.config.neo4j.uri)

        except ServiceUnavailable as e:
            raise GraphConnectionError(
                f"Failed to connect to Neo4j at {self.config.neo4j.uri}: {e}"
            ) from e

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            logger.info("neo4j_connection_closed")

    def execute_query(
        self, query: str, parameters: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        if not self.driver:
            raise GraphConnectionError("Not connected to Neo4j")

        try:
            with self.driver.session(
                database=self.config.neo4j.database
            ) as session:
                result = session.run(query, parameters or {})
                records = [dict(record) for record in result]

                logger.debug(
                    "query_executed",
                    query=query[:100],
                    params=bool(parameters),
                    results=len(records),
                )

                return records

        except Exception as e:
            logger.error("query_failed", query=query[:100], error=str(e))
            raise GraphConnectionError(f"Query execution failed: {e}") from e

    def create_node(
        self, label: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n
        """
        result = self.execute_query(query, {"properties": properties})
        return result[0]["n"] if result else {}

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        CREATE (source)-[r:{rel_type} $properties]->(target)
        RETURN r
        """
        params = {
            "source_id": source_id,
            "target_id": target_id,
            "properties": properties,
        }
        result = self.execute_query(query, params)
        return result[0]["r"] if result else {}

    def find_node(
        self, label: str, property_key: str, property_value: Any
    ) -> Optional[dict[str, Any]]:
        query = f"""
        MATCH (n:{label} {{{property_key}: $value}})
        RETURN n
        LIMIT 1
        """
        result = self.execute_query(query, {"value": property_value})
        return result[0]["n"] if result else None