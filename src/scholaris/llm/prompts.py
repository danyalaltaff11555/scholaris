
from pathlib import Path
from typing import Any

import yaml

from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class PromptManager:

    def __init__(self, prompts_path: str = "configs/prompts.yaml") -> None:
        self.prompts_path = Path(prompts_path)

        if not self.prompts_path.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_path}")

        with open(self.prompts_path, encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)

        logger.info("prompts_loaded", path=prompts_path)

    def get_prompt(self, category: str, prompt_type: str = "user_template") -> str:
        if category not in self.prompts:
            raise KeyError(f"Prompt category not found: {category}")

        if prompt_type not in self.prompts[category]:
            raise KeyError(
                f"Prompt type '{prompt_type}' not found in category '{category}'"
            )

        return self.prompts[category][prompt_type]

    def format_prompt(
        self, category: str, prompt_type: str = "user_template", **kwargs: Any
    ) -> str:
        template = self.get_prompt(category, prompt_type)
        formatted = template.format(**kwargs)

        logger.debug("prompt_formatted", category=category, type=prompt_type)

        return formatted
