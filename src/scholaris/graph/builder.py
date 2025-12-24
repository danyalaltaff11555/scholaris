
from typing import Optional

from scholaris.config import Config
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.types import Entity, Relation
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class GraphBuilder:

    def __init__(self, config: Config, neo4j_client: Neo4jClient) -> None:
        self.config = config
        self.client = neo4j_client

    def add_entity(self, entity: Entity) -> None:
        if not entity.id:
            logger.warning("entity_missing_id", text=entity.text)
            return

        properties = {
            "id": entity.id,
            "text": entity.text,
            "confidence": entity.confidence,
            **entity.metadata,
        }

        self.client.create_node(label=entity.type.value, properties=properties)
        logger.debug("entity_added", id=entity.id, type=entity.type.value)

    def add_relation(self, relation: Relation) -> None:
        properties = {
            "confidence": relation.confidence,
            **relation.metadata,
        }

        self.client.create_relationship(
            source_id=relation.source_id,
            target_id=relation.target_id,
            rel_type=relation.type.value,
            properties=properties,
        )
        logger.debug(
            "relation_added",
            source=relation.source_id,
            target=relation.target_id,
            type=relation.type.value,
        )

    def build_graph(
        self, entities: list[Entity], relations: list[Relation]
    ) -> None:
        logger.info("building_graph", entities=len(entities), relations=len(relations))

        for entity in entities:
            self.add_entity(entity)

        for relation in relations:
            self.add_relation(relation)

        logger.info("graph_built", entities=len(entities), relations=len(relations))

    def create_indexes(self) -> None:
        indexes = [
            "CREATE INDEX entity_id_index IF NOT EXISTS FOR (n:CONCEPT) ON (n.id)",
            "CREATE INDEX author_id_index IF NOT EXISTS FOR (n:AUTHOR) ON (n.id)",
            "CREATE INDEX paper_id_index IF NOT EXISTS FOR (n:PAPER) ON (n.id)",
        ]

        for index_query in indexes:
            try:
                self.client.execute_query(index_query)
                logger.info("index_created", query=index_query[:50])
            except Exception as e:
                logger.error("index_creation_failed", query=index_query[:50], error=str(e))
