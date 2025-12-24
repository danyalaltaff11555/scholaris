
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

from scholaris.utils.helpers import generate_id
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class DocumentLoadError(Exception):

    pass


def load_pdf(file_path: Path) -> str:
    try:
        reader = PdfReader(file_path)
        text_parts = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)
        logger.info(
            "loaded_pdf",
            file=file_path.name,
            pages=len(reader.pages),
            chars=len(full_text),
        )
        return full_text

    except Exception as e:
        raise DocumentLoadError(f"Failed to load PDF {file_path}: {e}") from e


def load_text(file_path: Path) -> str:
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        logger.info("loaded_text", file=file_path.name, chars=len(content))
        return content

    except Exception as e:
        raise DocumentLoadError(f"Failed to load text file {file_path}: {e}") from e


def load_markdown(file_path: Path) -> str:
    return load_text(file_path)


def load_document(file_path: str) -> tuple[str, str]:
    path = Path(file_path)

    if not path.exists():
        raise DocumentLoadError(f"File not found: {file_path}")

    if not path.is_file():
        raise DocumentLoadError(f"Not a file: {file_path}")

    suffix = path.suffix.lower()
    loaders = {
        ".pdf": load_pdf,
        ".txt": load_text,
        ".md": load_markdown,
        ".markdown": load_markdown,
    }

    loader = loaders.get(suffix)
    if not loader:
        raise ValueError(
            f"Unsupported file type: {suffix}. "
            f"Supported types: {list(loaders.keys())}"
        )

    content = loader(path)
    document_id = generate_id(f"{path.name}_{path.stat().st_mtime}")

    return document_id, content
