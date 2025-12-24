
import hashlib
from typing import Any


def generate_id(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def safe_get(dictionary: dict[str, Any], key: str, default: Any = None) -> Any:
    return dictionary.get(key, default)


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
