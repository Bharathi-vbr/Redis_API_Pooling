import json
import redis
from typing import Any, Dict, Optional

from config import REDIS_HOST, REDIS_PORT, REDIS_DB, CACHE_TTL

_redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
)

def _key(location: str) -> str:
    return f"weather:{location}"

def get_weather(location: str) -> Optional[Dict[str, Any]]:
    """Redis GET: return deserialized weather data or None."""
    raw = _redis.get(_key(location))
    return json.loads(raw) if raw else None

def set_weather(location: str, data: Dict[str, Any]) -> None:
    """Redis SET: create new entry with TTL."""
    _redis.setex(_key(location), CACHE_TTL, json.dumps(data))

def update_weather(location: str, data: Dict[str, Any]) -> None:
    """
    Redis UPDATE: upsert semantics.
    If key exists, overwrite value + TTL; if not, create.
    """
    set_weather(location, data)
