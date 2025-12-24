from typing import Any, Optional

from scholaris.config import Config
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.types import GraphEdge, GraphNode, GraphPath
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class GraphTraversal:
    def __init__(self, config: Config, neo4j_client: Neo4jClient) -> None:
        self.config = config
        self.client = neo4j_client

    def find_shortest_path(
        self, source_id: str, target_id: str, max_hops: Optional[int] = None
    ) -> Optional[GraphPath]:
        hops = max_hops or self.config.graph.max_hops

        query = """
        MATCH path = shortestPath(
            (source {id: $source_id})-[*..%d]-(target {id: $target_id})
        )
        RETURN nodes(path) as nodes, relationships(path) as edges
        """ % hops

        params = {"source_id": source_id, "target_id": target_id}

        results = self.client.execute_query(query, params)

        if not results:
            return None

        return self._build_graph_path(results[0])

    def find_related_entities(
        self,
        entity_id: str,
        relation_types: Optional[list[str]] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        if relation_types:
            rel_filter = "|".join(relation_types)
            query = f"""
            MATCH (source {{id: $entity_id}})-[r:{rel_filter}]-(target)
            RETURN target, type(r) as relation_type
            LIMIT $limit
            """
        else:
            query = """
            MATCH (source {id: $entity_id})-[r]-(target)
            RETURN target, type(r) as relation_type
            LIMIT $limit
            """

        params = {"entity_id": entity_id, "limit": limit}
        return self.client.execute_query(query, params)

    def search_entities_by_text(
        self,
        search_text: str,
        entity_types: Optional[list[str]] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        if entity_types:
            label_filter = "|".join(entity_types)
            query = f"""
            MATCH (n:{label_filter})
            WHERE toLower(n.text) CONTAINS toLower($search_text)
            RETURN n
            LIMIT $limit
            """
        else:
            query = """
            MATCH (n)
            WHERE toLower(n.text) CONTAINS toLower($search_text)
            RETURN n
            LIMIT $limit
            """

        params = {"search_text": search_text, "limit": limit}
        return self.client.execute_query(query, params)

    def _build_graph_path(self, result: dict[str, Any]) -> GraphPath:
        nodes = [
            GraphNode(
                id=node.get("id", ""),
                label=list(node.labels)[0] if node.labels else "",
                properties=dict(node),
            )
            for node in result.get("nodes", [])
        ]

        edges = [
            GraphEdge(
                source=edge.start_node.get("id", ""),
                target=edge.end_node.get("id", ""),
                type=edge.type,
                properties=dict(edge),
            )
            for edge in result.get("edges", [])
        ]

        return GraphPath(nodes=nodes, edges=edges, length=len(edges))
