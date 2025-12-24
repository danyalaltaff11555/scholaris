
import logging
import sys
from typing import Any


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("scholaris")
    logger.setLevel(getattr(logging, log_level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level.upper()))

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"scholaris.{name}")


class StructuredLogger:

    def __init__(self, name: str) -> None:
        self.logger = get_logger(name)

    def _format_message(self, message: str, **kwargs: Any) -> str:
        if kwargs:
            kv_pairs = " ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {kv_pairs}"
        return message

    def debug(self, message: str, **kwargs: Any) -> None:
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self.logger.error(self._format_message(message, **kwargs))
