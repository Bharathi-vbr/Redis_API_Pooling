Flight Polling Service (Aviationstack + Redis)
This project is a Python service that periodically polls the Aviationstack Flights API and caches multiple flights in Redis.

It demonstrates:

Redis get, set, and update operations via a thin client wrapper.​

API polling against an external API (Aviationstack /v1/flights).​

Creating or updating a Redis entry for each API result.​

A small, modular design that is easy to configure and extend.

High‑Level Architecture
At a high level:

The Python Flight Poller runs on a schedule and calls Aviationstack’s /v1/flights endpoint with configurable filters (dep_iata, arr_iata, flight_status, limit).​

The service normalizes the response into compact JSON snapshots per flight.

Each snapshot is stored in Redis under a key like flight:<flight_iata>. On each poll, the key is either created (if missing) or updated (if it already exists).​

Consumers (CLI, scripts, services) can read the latest flight status directly from Redis without hitting the external API.

Project Structure
text
Redis_API_Pooling/
├─ config.py          # Configuration (Redis, filters, polling interval, API key)
├─ api_client.py      # ApiClient: HTTP calls to Aviationstack, fetch_flights()
├─ redis_client.py    # RedisClient: get_value, set_value, update_value
├─ main.py            # Orchestration: scheduler loop, poll_and_cache_flights()
├─ venv/              # (Optional) Python virtual environment
└─ README.md
Modules:

config.py

Centralized configuration.

Reads AVIATIONSTACK_ACCESS_KEY from environment variables (no secrets hardcoded).​

Defines Redis connection (REDIS_HOST, REDIS_PORT, REDIS_DB), Aviationstack base URL, filters (DEP_IATA, ARR_IATA, FLIGHT_STATUS, MAX_FLIGHTS), polling interval, and key template (REDIS_FLIGHT_KEY_TEMPLATE).​

api_client.py

ApiClient uses requests to call Aviationstack /v1/flights.​

fetch_flights() builds the request, parses the data array, and returns a list of compact flight dicts with fields like flight_iata, airline_name, status, departure/arrival info, and last_polled_ts.

redis_client.py

RedisClient wraps redis-py (redis.Redis) and exposes:​

get_value(key) – reads the current value (or None).

set_value(key, value) – creates/overwrites a key.

update_value(key, value) – updates an existing key (implemented as a SET for strings).

main.py

Creates RedisClient and ApiClient using config.py.

poll_and_cache_flights() fetches flights from Aviationstack, then for each flight:

Builds key flight:<flight_iata>.

Calls get_value(key); if None, uses set_value; otherwise update_value.

main() runs an infinite scheduler loop: call poll_and_cache_flights() → sleep(POLL_INTERVAL_SECONDS).

Setup Instructions
1. Prerequisites
Python 3 (e.g., from Homebrew).​

Redis running locally (Mac example with Homebrew):​

bash
brew install redis
brew services start redis
redis-cli ping   # should print PONG
Aviationstack account and API key (free tier is enough).​

2. Clone and create a virtual environment
bash
cd /path/to
git clone <your-repo-url> Redis_API_Pooling
cd Redis_API_Pooling

python3 -m venv venv
source venv/bin/activate
3. Install dependencies
bash
pip install --upgrade pip
pip install redis requests
This installs redis-py and requests.​

4. Configure environment variables
Export your Aviationstack API key:

bash
echo 'export AVIATIONSTACK_ACCESS_KEY="YOUR_REAL_ACCESS_KEY"' >> ~/.zshrc
source ~/.zshrc
Optional: override defaults for filters or Redis connection:

bash
export DEP_IATA="WUH"
export ARR_IATA="SZX"
export FLIGHT_STATUS="scheduled"
export MAX_FLIGHTS="5"
export POLL_INTERVAL_SECONDS="60"
# export REDIS_HOST="localhost"
# export REDIS_PORT="6379"
# export REDIS_DB="0"
config.py reads these values at startup.​

Running the Service
With the virtualenv active and Redis running:

bash
python main.py
You should see log output similar to:

Starting multi-flight polling loop. Interval=60s, dep_iata=..., arr_iata=..., status=...

Polling Aviationstack API for flights dep_iata=..., arr_iata=..., status=...

For each flight:

Key 'flight:MU2557' does not exist yet. Creating it.

Key 'flight:MU2557' now holds: {...}

On subsequent polls: Key 'flight:MU2557' exists. Updating it.

This shows the get/set/update cycle per flight.

Inspecting Data in Redis
In another terminal:

bash
redis-cli -n 0 KEYS "flight:*"
Example output:

text
1) "flight:MU2557"
2) "flight:CA1234"
...
To view a specific flight:

bash
redis-cli -n 0 GET "flight:MU2557"
You should see a JSON string like:

json
{
  "flight_iata": "MU2557",
  "flight_number": "2557",
  "airline_name": "China Eastern Airlines",
  "status": "scheduled",
  "departure_airport": "Tianhe International",
  "departure_iata": "WUH",
  "departure_scheduled": "2025-12-14T15:15:00+00:00",
  "arrival_airport": "Shenzhen",
  "arrival_iata": "SZX",
  "arrival_scheduled": "2025-12-14T17:20:00+00:00",
  "last_polled_ts": 1765726363
}
This shows that Redis holds one JSON snapshot per flight key, updated on each poll.​

Configuration and Extensibility
Configuration and secrets

Environment variables control all runtime configuration (API key, Redis host/port/DB, filters, polling interval).​

No secrets are committed to source control.

Changing which flights are tracked

Adjust DEP_IATA, ARR_IATA, FLIGHT_STATUS, and MAX_FLIGHTS via environment variables or directly in config.py.​

Swapping APIs or data sources

Replace ApiClient and related config while keeping RedisClient and the orchestration logic in main.py.

The pattern “poll external API → normalize → cache in Redis” remains the same.

Possible Future Enhancements
Add TTLs on Redis keys to automatically expire stale flight entries.​

Add a simple HTTP API (e.g., FastAPI) on top of Redis for serving flight data.​

Add metrics and monitoring (e.g., Prometheus, CloudWatch) for poll latency, API errors, and cache statistics.​

