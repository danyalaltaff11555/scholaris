
from typing import Optional

from scholaris.config import Config
from scholaris.types import Entity, Relation, RelationType
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class RelationExtractor:

    def __init__(self, config: Config) -> None:
        self.config = config
        self.confidence_threshold = config.extraction.relation_confidence_threshold

    def extract_relations(
        self, text: str, entities: list[Entity]
    ) -> list[Relation]:
        relations = []

        relations.extend(self._extract_proximity_relations(text, entities))

        filtered_relations = [
            r for r in relations if r.confidence >= self.confidence_threshold
        ]

        logger.info(
            "relations_extracted",
            total=len(relations),
            filtered=len(filtered_relations),
            threshold=self.confidence_threshold,
        )

        return filtered_relations

    def _extract_proximity_relations(
        self, text: str, entities: list[Entity]
    ) -> list[Relation]:
        relations = []

        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1 : i + 3]:
                if entity1.id and entity2.id:
                    relation = Relation(
                        source_id=entity1.id,
                        target_id=entity2.id,
                        type=RelationType.MENTIONS,
                        confidence=0.7,
                        metadata={"method": "proximity"},
                    )
                    relations.append(relation)

        return relations

    def filter_by_confidence(
        self, relations: list[Relation], min_confidence: float
    ) -> list[Relation]:
        filtered = [r for r in relations if r.confidence >= min_confidence]

        logger.info(
            "relations_filtered",
            original=len(relations),
            filtered=len(filtered),
            threshold=min_confidence,
        )

        return filtered
