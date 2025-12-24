
from typing import Optional

import anthropic
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from scholaris.config import Config
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class LLMClient:

    def __init__(self, config: Config) -> None:
        self.config = config

        if config.llm.provider == "anthropic":
            if not config.app.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            self.client = anthropic.Anthropic(api_key=config.app.anthropic_api_key)

        elif config.llm.provider == "openai":
            if not config.app.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = openai.OpenAI(api_key=config.app.openai_api_key)

        else:
            raise ValueError(f"Unsupported LLM provider: {config.llm.provider}")

        logger.info("llm_client_initialized", provider=config.llm.provider)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
    )
    def generate(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> str:
        try:
            if self.config.llm.provider == "anthropic":
                return self._generate_anthropic(prompt, system_prompt)
            else:
                return self._generate_openai(prompt, system_prompt)

        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            raise

    def _generate_anthropic(
        self, prompt: str, system_prompt: Optional[str]
    ) -> str:
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.config.llm.model,
            "max_tokens": self.config.llm.max_tokens,
            "temperature": self.config.llm.temperature,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        text = response.content[0].text

        logger.info(
            "llm_generated",
            provider="anthropic",
            tokens=response.usage.output_tokens,
        )

        return text

    def _generate_openai(
        self, prompt: str, system_prompt: Optional[str]
    ) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=messages,
            max_tokens=self.config.llm.max_tokens,
            temperature=self.config.llm.temperature,
        )

        text = response.choices[0].message.content or ""

        logger.info(
            "llm_generated",
            provider="openai",
            tokens=response.usage.completion_tokens,
        )

        return text
