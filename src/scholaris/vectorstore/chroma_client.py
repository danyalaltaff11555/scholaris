
from typing import Any, Optional

import chromadb
from chromadb.config import Settings

from scholaris.config import Config
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class ChromaClient:

    def __init__(self, config: Config) -> None:
        self.config = config

        settings = Settings(
            persist_directory=config.chroma.persist_directory,
            anonymized_telemetry=False,
        )

        self.client = chromadb.Client(settings)
        self.collection = self._get_or_create_collection()

        logger.info("chroma_initialized", collection=config.chroma.collection_name)

    def _get_or_create_collection(self) -> chromadb.Collection:
        return self.client.get_or_create_collection(
            name=self.config.chroma.collection_name
        )

    def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info("embeddings_added", count=len(ids))

    def search(
        self, query_embedding: list[float], n_results: int = 5
    ) -> dict[str, Any]:
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        logger.info("search_completed", results=n_results)
        return results

    def delete_collection(self) -> None:
        self.client.delete_collection(name=self.config.chroma.collection_name)
        logger.info("collection_deleted")
