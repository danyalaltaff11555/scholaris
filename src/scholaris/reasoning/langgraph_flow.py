
from typing import Any

from scholaris.config import Config
from scholaris.types import ReasoningState
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class LangGraphFlow:

    def __init__(self, config: Config) -> None:
        self.config = config

    def create_initial_state(self, query: str) -> ReasoningState:
        return ReasoningState(query=query)

    def should_continue(self, state: ReasoningState) -> bool:
        if state.is_complete:
            return False

        if len(state.reasoning_steps) >= self.config.reasoning.max_steps:
            return False

        return True

    def execute_workflow(self, query: str) -> ReasoningState:
        state = self.create_initial_state(query)

        logger.info("workflow_started", query=query)

        state.is_complete = True

        logger.info(
            "workflow_completed",
            steps=len(state.reasoning_steps),
            has_answer=bool(state.current_answer),
        )

        return state
