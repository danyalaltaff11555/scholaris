
from typing import Optional

from scholaris.config import Config
from scholaris.types import Entity, EntityType
from scholaris.utils.helpers import generate_id, normalize_text
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class EntityExtractor:

    def __init__(self, config: Config) -> None:
        self.config = config
        self.confidence_threshold = config.extraction.entity_confidence_threshold

    def extract_entities(self, text: str) -> list[Entity]:
        entities = []

        entities.extend(self._extract_simple_patterns(text))

        filtered_entities = [
            e for e in entities if e.confidence >= self.confidence_threshold
        ]

        logger.info(
            "entities_extracted",
            total=len(entities),
            filtered=len(filtered_entities),
            threshold=self.confidence_threshold,
        )

        return filtered_entities

    def _extract_simple_patterns(self, text: str) -> list[Entity]:
        entities = []

        words = text.split()
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 3:
                entity_text = word
                entity_id = generate_id(normalize_text(entity_text))

                entity = Entity(
                    id=entity_id,
                    text=entity_text,
                    type=EntityType.CONCEPT,
                    confidence=0.8,
                    metadata={"position": i},
                )
                entities.append(entity)

        return entities

    def deduplicate_entities(self, entities: list[Entity]) -> list[Entity]:
        seen = set()
        unique_entities = []

        for entity in entities:
            normalized = normalize_text(entity.text)
            if normalized not in seen:
                seen.add(normalized)
                unique_entities.append(entity)

        logger.info(
            "entities_deduplicated",
            original=len(entities),
            unique=len(unique_entities),
        )

        return unique_entities
