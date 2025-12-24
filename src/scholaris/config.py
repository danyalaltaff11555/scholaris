from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    provider: str = Field(default="anthropic")
    model: str = Field(default="claude-sonnet-4")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    timeout: int = Field(default=60, gt=0)


class Neo4jConfig(BaseSettings):
    uri: str = Field(default="bolt://localhost:7687")
    user: str = Field(default="neo4j")
    password: str = Field(default="password")
    database: str = Field(default="scholaris")
    max_connection_lifetime: int = Field(default=3600)
    max_connection_pool_size: int = Field(default=50)

    model_config = SettingsConfigDict(env_prefix="NEO4J_")


class RedisConfig(BaseSettings):
    url: str = Field(default="redis://localhost:6379")
    password: str = Field(default="")
    ttl: int = Field(default=3600, gt=0)
    max_connections: int = Field(default=10, gt=0)

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class ChromaConfig(BaseSettings):
    persist_directory: str = Field(default="./data/chroma")
    collection_name: str = Field(default="scholaris_embeddings")

    model_config = SettingsConfigDict(env_prefix="CHROMA_")


class ContextConfig(BaseSettings):
    max_tokens: int = Field(default=3000, gt=0)
    summarization_trigger: int = Field(default=2500, gt=0)
    history_window: int = Field(default=10, gt=0)


class GraphConfig(BaseSettings):
    max_hops: int = Field(default=3, ge=1, le=10)
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    entity_types: list[str] = Field(
        default_factory=lambda: [
            "CONCEPT",
            "AUTHOR",
            "PAPER",
            "METHOD",
            "DATASET",
            "THEORY",
        ]
    )
    relation_types: list[str] = Field(
        default_factory=lambda: [
            "DEFINES",
            "USES",
            "CITES",
            "AUTHORED",
            "PROPOSES",
            "VALIDATES",
            "CONTRADICTS",
            "EXTENDS",
        ]
    )


class ReasoningConfig(BaseSettings):
    max_steps: int = Field(default=5, ge=1, le=20)
    verify_consistency: bool = Field(default=True)
    show_intermediate: bool = Field(default=True)
    enable_fallback: bool = Field(default=True)


class ExtractionConfig(BaseSettings):
    batch_size: int = Field(default=32, gt=0)
    entity_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    relation_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class EmbeddingsConfig(BaseSettings):
    model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    dimension: int = Field(default=384, gt=0)
    batch_size: int = Field(default=32, gt=0)


class AppConfig(BaseSettings):
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")

    anthropic_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class Config:
    def __init__(self, config_path: str = "configs/config.yaml") -> None:
        self.app = AppConfig()

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        self.llm = self._load_section(LLMConfig, yaml_config.get("llm", {}))
        self.neo4j = Neo4jConfig()
        self.redis = RedisConfig()
        self.chroma = self._load_section(ChromaConfig, yaml_config.get("chroma", {}))
        self.context = self._load_section(
            ContextConfig, yaml_config.get("context", {})
        )
        self.graph = self._load_section(GraphConfig, yaml_config.get("graph", {}))
        self.reasoning = self._load_section(
            ReasoningConfig, yaml_config.get("reasoning", {})
        )
        self.extraction = self._load_section(
            ExtractionConfig, yaml_config.get("extraction", {})
        )
        self.embeddings = self._load_section(
            EmbeddingsConfig, yaml_config.get("embeddings", {})
        )

        self._validate_configuration()

    def _load_section(
        self, config_class: type[BaseSettings], yaml_data: dict[str, Any]
    ) -> BaseSettings:
        return config_class(**yaml_data)

    def _validate_configuration(self) -> None:
        if self.context.summarization_trigger >= self.context.max_tokens:
            raise ValueError(
                f"Summarization trigger ({self.context.summarization_trigger}) "
                f"must be less than max tokens ({self.context.max_tokens})"
            )

        if self.llm.provider not in ["anthropic", "openai"]:
            raise ValueError(
                f"Unsupported LLM provider: {self.llm.provider}. "
                "Must be 'anthropic' or 'openai'"
            )


def load_config(config_path: str = "configs/config.yaml") -> Config:
    return Config(config_path)
