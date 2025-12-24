"""Tests for reasoning modules."""

from scholaris.reasoning.cot_engine import ChainOfThoughtEngine
from scholaris.reasoning.query_analyzer import QueryAnalyzer
from scholaris.types import QueryIntent


def test_query_analysis(config, sample_query):
    """Test query analysis."""
    analyzer = QueryAnalyzer(config)
    analysis = analyzer.analyze_query(sample_query)

    assert analysis.intent in QueryIntent
    assert isinstance(analysis.key_entities, list)
    assert isinstance(analysis.sub_queries, list)


def test_reasoning_steps_generation(config, sample_query):
    """Test reasoning steps generation."""
    engine = ChainOfThoughtEngine(config)
    steps = engine.generate_reasoning_steps(sample_query, "Sample context")

    assert len(steps) > 0
    assert all(step.step_number > 0 for step in steps)


def test_reasoning_consistency_verification(config):
    """Test reasoning consistency verification."""
    engine = ChainOfThoughtEngine(config)
    steps = engine.generate_reasoning_steps("Test query", "Test context")

    is_consistent = engine.verify_consistency(steps)
    assert isinstance(is_consistent, bool)
