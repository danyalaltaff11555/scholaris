
from pathlib import Path
from typing import Optional

from scholaris.ingestion.chunker import chunk_text
from scholaris.ingestion.loader import load_document
from scholaris.types import DocumentChunk
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class IngestionPipeline:

    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def process_document(self, file_path: str) -> tuple[str, list[DocumentChunk]]:
        logger.info("processing_document", file=file_path)

        document_id, content = load_document(file_path)

        chunks = chunk_text(
            text=content,
            document_id=document_id,
            chunk_size=self.chunk_size,
            overlap=self.overlap,
        )

        logger.info(
            "document_processed",
            document_id=document_id,
            chunks=len(chunks),
            total_chars=len(content),
        )

        return document_id, chunks

    def process_directory(self, directory_path: str) -> dict[str, list[DocumentChunk]]:
        directory = Path(directory_path)

        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")

        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")

        supported_extensions = {".pdf", ".txt", ".md", ".markdown"}
        results = {}

        for file_path in directory.rglob("*"):
            if file_path.suffix.lower() in supported_extensions:
                try:
                    document_id, chunks = self.process_document(str(file_path))
                    results[document_id] = chunks
                except Exception as e:
                    logger.error("document_processing_failed", file=str(file_path), error=str(e))

        logger.info("directory_processed", total_documents=len(results))
        return results
