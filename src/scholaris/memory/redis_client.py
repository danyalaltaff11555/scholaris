
import json
from typing import Any, Optional

import redis

from scholaris.config import Config
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class RedisClient:

    def __init__(self, config: Config) -> None:
        self.config = config

        redis_config = {
            "decode_responses": True,
            "max_connections": config.redis.max_connections,
        }

        if config.redis.password:
            redis_config["password"] = config.redis.password

        self.client = redis.from_url(config.redis.url, **redis_config)

        self._test_connection()
        logger.info("redis_connected", url=config.redis.url)

    def _test_connection(self) -> None:
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        serialized = json.dumps(value)
        expire_time = ttl or self.config.redis.ttl

        self.client.setex(key, expire_time, serialized)
        logger.debug("redis_set", key=key, ttl=expire_time)

    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)

        if value:
            logger.debug("redis_hit", key=key)
            return json.loads(value)

        logger.debug("redis_miss", key=key)
        return None

    def delete(self, key: str) -> None:
        self.client.delete(key)
        logger.debug("redis_delete", key=key)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def clear_pattern(self, pattern: str) -> int:
        keys = list(self.client.scan_iter(match=pattern))
        if keys:
            deleted = self.client.delete(*keys)
            logger.info("redis_pattern_cleared", pattern=pattern, deleted=deleted)
            return deleted
        return 0
