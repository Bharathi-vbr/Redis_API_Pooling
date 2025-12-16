# redis_client.py

import redis
from typing import Optional


class RedisClient:
    def __init__(self, host: str, port: int, db: int = 0) -> None:
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
        )

    def get_value(self, key: str) -> Optional[str]:
        """Return value for key or None if not present."""
        return self._client.get(key)

    def set_value(self, key: str, value: str) -> None:
        """Create or overwrite a key with the given string value."""
        self._client.set(key, value)

    def update_value(self, key: str, value: str) -> None:
        """
        Update an existing key.
        For string values, this is effectively the same as set.
        """
        self._client.set(key, value)
