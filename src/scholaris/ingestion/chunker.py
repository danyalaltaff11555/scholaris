
from typing import Optional

from scholaris.types import DocumentChunk
from scholaris.utils.helpers import generate_id
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200


def chunk_text(
    text: str,
    document_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError(f"Chunk size must be positive, got {chunk_size}")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            f"Overlap must be between 0 and chunk_size ({chunk_size}), got {overlap}"
        )

    if not text:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]

        chunk_id = generate_id(f"{document_id}_{chunk_index}")

        chunk = DocumentChunk(
            id=chunk_id,
            document_id=document_id,
            text=chunk_text,
            start_char=start,
            end_char=end,
            metadata={"chunk_index": chunk_index},
        )
        chunks.append(chunk)

        chunk_index += 1
        start = end - overlap

        if end >= len(text):
            break

    logger.info(
        "chunked_text",
        document_id=document_id,
        total_chunks=len(chunks),
        avg_size=sum(len(c.text) for c in chunks) // len(chunks) if chunks else 0,
    )

    return chunks


def chunk_by_sentences(
    text: str, document_id: str, max_sentences: int = 5
) -> list[DocumentChunk]:
    sentences = text.split(". ")
    chunks = []
    chunk_index = 0
    start_char = 0

    for i in range(0, len(sentences), max_sentences):
        sentence_group = sentences[i : i + max_sentences]
        chunk_text = ". ".join(sentence_group)

        if not chunk_text.endswith("."):
            chunk_text += "."

        end_char = start_char + len(chunk_text)
        chunk_id = generate_id(f"{document_id}_{chunk_index}")

        chunk = DocumentChunk(
            id=chunk_id,
            document_id=document_id,
            text=chunk_text,
            start_char=start_char,
            end_char=end_char,
            metadata={"chunk_index": chunk_index, "sentences": len(sentence_group)},
        )
        chunks.append(chunk)

        chunk_index += 1
        start_char = end_char

    return chunks
