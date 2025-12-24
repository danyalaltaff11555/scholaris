"""Tests for extraction modules."""

from scholaris.extraction.entities import EntityExtractor
from scholaris.extraction.linker import EntityLinker
from scholaris.types import Entity, EntityType


def test_entity_extraction(config, sample_text):
    """Test entity extraction."""
    extractor = EntityExtractor(config)
    entities = extractor.extract_entities(sample_text)

    assert isinstance(entities, list)


def test_entity_deduplication(config):
    """Test entity deduplication."""
    extractor = EntityExtractor(config)

    entities = [
        Entity(id="1", text="Machine Learning", type=EntityType.CONCEPT),
        Entity(id="2", text="machine learning", type=EntityType.CONCEPT),
    ]

    unique = extractor.deduplicate_entities(entities)
    assert len(unique) == 1


def test_entity_linking():
    """Test entity linking."""
    linker = EntityLinker()

    entity1 = Entity(id="1", text="Machine Learning", type=EntityType.CONCEPT)
    entity2 = Entity(id="2", text="machine learning", type=EntityType.CONCEPT)

    id1 = linker.link_entity(entity1)
    id2 = linker.link_entity(entity2)

    assert id1 == id2
