# config.py
import os

# Redis connection
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Aviationstack API
API_BASE_URL = "http://api.aviationstack.com/v1"
AVIATIONSTACK_ACCESS_KEY = os.getenv("AVIATIONSTACK_ACCESS_KEY")

if not AVIATIONSTACK_ACCESS_KEY:
    raise RuntimeError(
        "AVIATIONSTACK_ACCESS_KEY environment variable is not set. "
        "Export it before running main.py."
    )

# Filters to get MULTIPLE flights
# Example: all scheduled flights from WUH to SZX (adjust as you like)
DEP_IATA = "WUH"   # departure airport IATA
ARR_IATA = "SZX"   # arrival airport IATA
FLIGHT_STATUS = "scheduled"  # e.g. 'scheduled', 'active', 'landed'
MAX_FLIGHTS = 5    # how many flights to store per poll (limit)

# Polling and Redis key template
POLL_INTERVAL_SECONDS = 60
# Key will look like: flight:MU2557 or flight:WUH:SZX:MU2557
REDIS_FLIGHT_KEY_TEMPLATE = "flight:{flight_iata}"
