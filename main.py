# main.py

import json
import time
import logging

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    API_BASE_URL,
    AVIATIONSTACK_ACCESS_KEY,
    DEP_IATA,
    ARR_IATA,
    FLIGHT_STATUS,
    POLL_INTERVAL_SECONDS,
    REDIS_FLIGHT_KEY_TEMPLATE,
)
from redis_client import RedisClient
from api_client import ApiClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def build_flight_key(flight_iata: str) -> str:
    """
    Build a Redis key for a flight, e.g. flight:MU2557.
    You can customize this to include airports if you want.
    """
    return REDIS_FLIGHT_KEY_TEMPLATE.format(flight_iata=flight_iata)


def poll_and_cache_flights(redis_client: RedisClient, api_client: ApiClient) -> None:
    """
    Poll Aviationstack for multiple flights and cache each one in Redis.
    """
    try:
        logging.info(
            "Polling Aviationstack API for flights dep_iata=%s, arr_iata=%s, status=%s",
            DEP_IATA,
            ARR_IATA,
            FLIGHT_STATUS,
        )

        flights = api_client.fetch_flights()

        if not flights:
            logging.warning(
                "No flights returned for dep_iata=%s, arr_iata=%s, status=%s; nothing to cache.",
                DEP_IATA,
                ARR_IATA,
                FLIGHT_STATUS,
            )
            return

        for flight in flights:
            flight_iata = flight["flight_iata"]
            key = build_flight_key(flight_iata)
            serialized = json.dumps(flight)

            existing = redis_client.get_value(key)
            if existing is None:
                logging.info("Key '%s' does not exist yet. Creating it.", key)
                redis_client.set_value(key, serialized)
            else:
                logging.info("Key '%s' exists. Updating it.", key)
                redis_client.update_value(key, serialized)

            logging.info("Key '%s' now holds: %s", key, serialized)

    except Exception as exc:
        logging.error("Failed to poll Aviationstack or update Redis: %s", exc)


def main() -> None:
    redis_client = RedisClient(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
    )
    api_client = ApiClient(API_BASE_URL, AVIATIONSTACK_ACCESS_KEY)

    logging.info(
        "Starting multi-flight polling loop. Interval=%ss, dep_iata=%s, arr_iata=%s, status=%s",
        POLL_INTERVAL_SECONDS,
        DEP_IATA,
        ARR_IATA,
        FLIGHT_STATUS,
    )
    while True:
        poll_and_cache_flights(redis_client, api_client)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
