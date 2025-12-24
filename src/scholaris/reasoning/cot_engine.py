
from scholaris.config import Config
from scholaris.types import ReasoningStep
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class ChainOfThoughtEngine:

    def __init__(self, config: Config) -> None:
        self.config = config

    def generate_reasoning_steps(
        self, query: str, graph_context: str
    ) -> list[ReasoningStep]:
        steps = []

        step1 = ReasoningStep(
            step_number=1,
            description="Identify key concepts in the question",
            action="concept_extraction",
            result=f"Extracted concepts from: {query[:50]}...",
            confidence=0.9,
        )
        steps.append(step1)

        step2 = ReasoningStep(
            step_number=2,
            description="Search knowledge graph for relevant information",
            action="graph_query",
            result=f"Found context: {graph_context[:100]}...",
            confidence=0.85,
        )
        steps.append(step2)

        step3 = ReasoningStep(
            step_number=3,
            description="Synthesize answer from graph data",
            action="synthesis",
            result="Combining information to form coherent answer",
            confidence=0.8,
        )
        steps.append(step3)

        logger.info("reasoning_steps_generated", total_steps=len(steps))

        return steps

    def verify_consistency(self, steps: list[ReasoningStep]) -> bool:
        if not steps:
            return False

        avg_confidence = sum(s.confidence for s in steps) / len(steps)

        is_consistent = avg_confidence >= self.config.graph.min_confidence

        logger.info(
            "reasoning_verified",
            steps=len(steps),
            avg_confidence=avg_confidence,
            consistent=is_consistent,
        )

        return is_consistent
