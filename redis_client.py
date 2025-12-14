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
        return self._client.get(key)

    def set_value(self, key: str, value: str) -> None:
        self._client.set(key, value)

    def update_value(self, key: str, value: str) -> None:
        # For simple string values, update is just overwrite.
        self._client.set(key, value)
