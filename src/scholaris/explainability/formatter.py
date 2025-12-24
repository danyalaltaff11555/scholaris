
from scholaris.types import ReasoningStep, Source
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class ReasoningFormatter:

    def format_reasoning_trace(self, steps: list[ReasoningStep]) -> str:
        if not steps:
            return "No reasoning steps available."

        lines = ["## Reasoning Trace\n"]

        for step in steps:
            lines.append(f"**Step {step.step_number}: {step.description}**")
            lines.append(f"- Action: {step.action}")
            lines.append(f"- Result: {step.result}")
            lines.append(f"- Confidence: {step.confidence:.2f}\n")

        formatted = "\n".join(lines)

        logger.debug("reasoning_trace_formatted", steps=len(steps))

        return formatted

    def format_sources(self, sources: list[Source]) -> str:
        if not sources:
            return "No sources cited."

        lines = ["## Sources\n"]

        for i, source in enumerate(sources, start=1):
            citation = f"{i}. **{source.title}**"

            if source.page:
                citation += f" (Page {source.page})"

            citation += f" - Confidence: {source.confidence:.2f}"

            lines.append(citation)

        formatted = "\n".join(lines)

        logger.debug("sources_formatted", count=len(sources))

        return formatted

    def format_complete_explanation(
        self,
        answer: str,
        reasoning_steps: list[ReasoningStep],
        sources: list[Source],
    ) -> str:
        sections = [
            "# Answer\n",
            answer,
            "\n\n",
            self.format_reasoning_trace(reasoning_steps),
            "\n",
            self.format_sources(sources),
        ]

        return "".join(sections)
