
from typing import Optional

from sentence_transformers import SentenceTransformer

from scholaris.config import Config
from scholaris.utils.helpers import chunk_list
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class Embedder:

    def __init__(self, config: Config) -> None:
        self.config = config
        self.model = SentenceTransformer(config.embeddings.model)
        self.cache: dict[str, list[float]] = {}

        logger.info("embedder_initialized", model=config.embeddings.model)

    def embed_text(self, text: str) -> list[float]:
        if text in self.cache:
            logger.debug("embedding_cache_hit", text_length=len(text))
            return self.cache[text]

        embedding = self.model.encode(text).tolist()
        self.cache[text] = embedding

        logger.debug("embedding_generated", text_length=len(text))
        return embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        uncached_texts = [t for t in texts if t not in self.cache]

        if uncached_texts:
            batches = chunk_list(uncached_texts, self.config.embeddings.batch_size)

            for batch in batches:
                embeddings = self.model.encode(batch)
                for text, embedding in zip(batch, embeddings):
                    self.cache[text] = embedding.tolist()

        results = [self.cache[text] for text in texts]

        logger.info(
            "batch_embeddings_generated",
            total=len(texts),
            cached=len(texts) - len(uncached_texts),
        )

        return results

    def clear_cache(self) -> None:
        cache_size = len(self.cache)
        self.cache.clear()
        logger.info("cache_cleared", entries=cache_size)
