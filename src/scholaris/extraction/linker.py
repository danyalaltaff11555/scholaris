
from typing import Optional

from scholaris.types import Entity
from scholaris.utils.helpers import normalize_text
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class EntityLinker:

    def __init__(self) -> None:
        self.entity_index: dict[str, Entity] = {}

    def link_entity(self, entity: Entity) -> str:
        normalized = normalize_text(entity.text)

        if normalized in self.entity_index:
            canonical = self.entity_index[normalized]
            logger.debug("entity_linked", text=entity.text, canonical_id=canonical.id)
            return canonical.id or entity.id or ""

        if entity.id:
            self.entity_index[normalized] = entity
            return entity.id

        return ""

    def link_entities(self, entities: list[Entity]) -> dict[str, str]:
        mapping = {}

        for entity in entities:
            if entity.id:
                canonical_id = self.link_entity(entity)
                mapping[entity.id] = canonical_id

        logger.info("entities_linked", total=len(entities), unique=len(self.entity_index))

        return mapping

    def get_canonical_entity(self, entity_text: str) -> Optional[Entity]:
        normalized = normalize_text(entity_text)
        return self.entity_index.get(normalized)
