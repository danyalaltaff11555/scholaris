"""
Document ingestion script.

CLI tool for ingesting documents into the knowledge graph.
"""

import argparse
from pathlib import Path

from scholaris.chatbot import ScholarisChatbot
from scholaris.config import load_config
from scholaris.utils.logging import setup_logging

logger = setup_logging("INFO")


def ingest_file(chatbot: ScholarisChatbot, file_path: str) -> None:
    """Ingest a single file."""
    logger.info(f"Ingesting file: {file_path}")

    result = chatbot.ingest_document(file_path)

    logger.info(
        f"Ingested {result['chunks']} chunks, "
        f"{result['entities']} entities, "
        f"{result['relations']} relations"
    )


def ingest_directory(chatbot: ScholarisChatbot, directory_path: str) -> None:
    """Ingest all documents in a directory."""
    directory = Path(directory_path)

    if not directory.exists():
        logger.error(f"Directory not found: {directory_path}")
        return

    supported_extensions = {".pdf", ".txt", ".md", ".markdown"}

    for file_path in directory.rglob("*"):
        if file_path.suffix.lower() in supported_extensions:
            try:
                ingest_file(chatbot, str(file_path))
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")


def main():
    """Main ingestion function."""
    parser = argparse.ArgumentParser(description="Ingest documents into Scholaris")

    parser.add_argument(
        "--path",
        required=True,
        help="Path to file or directory to ingest",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process directories",
    )

    args = parser.parse_args()

    config = load_config()
    chatbot = ScholarisChatbot(config)

    path = Path(args.path)

    if path.is_file():
        ingest_file(chatbot, str(path))
    elif path.is_dir():
        ingest_directory(chatbot, str(path))
    else:
        logger.error(f"Invalid path: {args.path}")

    chatbot.close()
    logger.info("Ingestion complete!")


if __name__ == "__main__":
    main()
