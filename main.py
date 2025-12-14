import json
import time
import logging

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    API_BASE_URL,
    TODO_ID,
    POLL_INTERVAL_SECONDS,
    REDIS_TODO_KEY_TEMPLATE,
)
from redis_client import RedisClient
from api_client import ApiClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def build_todo_key(todo_id: int) -> str:
    return REDIS_TODO_KEY_TEMPLATE.format(id=todo_id)


def poll_and_cache_todo(redis_client: RedisClient, api_client: ApiClient, todo_id: int) -> None:
    key = build_todo_key(todo_id)

    try:
        logging.info("Polling API for TODO id=%s", todo_id)
        todo_data = api_client.fetch_todo(todo_id)
        serialized = json.dumps(todo_data)

        existing = redis_client.get_value(key)
        if existing is None:
            logging.info("Key '%s' does not exist yet. Creating it.", key)
            redis_client.set_value(key, serialized)
        else:
            logging.info("Key '%s' exists. Updating it.", key)
            redis_client.update_value(key, serialized)

        logging.info("Key '%s' now holds: %s", key, serialized)

    except Exception as exc:
        logging.error("Failed to poll API or update Redis for key '%s': %s", key, exc)


def main() -> None:
    redis_client = RedisClient(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
    )
    api_client = ApiClient(API_BASE_URL)

    logging.info("Starting polling loop. Interval=%ss", POLL_INTERVAL_SECONDS)
    while True:
        poll_and_cache_todo(redis_client, api_client, TODO_ID)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
