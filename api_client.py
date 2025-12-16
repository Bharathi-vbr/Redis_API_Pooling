# api_client.py

import time
from typing import Dict, Any, List

import requests

from config import (
    API_BASE_URL,
    AVIATIONSTACK_ACCESS_KEY,
    DEP_IATA,
    ARR_IATA,
    FLIGHT_STATUS,
    MAX_FLIGHTS,
)


class ApiClient:
    def __init__(self, base_url: str, access_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_key = access_key

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal helper to perform a GET request to Aviationstack.
        """
        url = f"{self.base_url}{path}"
        merged_params = {"access_key": self.access_key}
        merged_params.update(params)

        response = requests.get(url, params=merged_params, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_flights(self) -> List[Dict[str, Any]]:
        """
        Fetch multiple flights using /flights with filters like dep_iata, arr_iata, status.

        Returns a list of compact dicts with selected fields plus last_polled_ts.
        """
        params: Dict[str, Any] = {
            "dep_iata": DEP_IATA,
            "arr_iata": ARR_IATA,
            "flight_status": FLIGHT_STATUS,
            "limit": MAX_FLIGHTS,
        }

        raw = self._get("/flights", params)
        data: List[Dict[str, Any]] = raw.get("data", []) or []

        flights: List[Dict[str, Any]] = []
        now_ts = int(time.time())

        for flight in data:
            airline = flight.get("airline", {}) or {}
            flight_info = flight.get("flight", {}) or {}
            departure = flight.get("departure", {}) or {}
            arrival = flight.get("arrival", {}) or {}

            compact = {
                "flight_iata": flight_info.get("iata"),
                "flight_number": flight_info.get("number"),
                "airline_name": airline.get("name"),
                "status": flight.get("flight_status"),
                "departure_airport": departure.get("airport"),
                "departure_iata": departure.get("iata"),
                "departure_scheduled": departure.get("scheduled"),
                "arrival_airport": arrival.get("airport"),
                "arrival_iata": arrival.get("iata"),
                "arrival_scheduled": arrival.get("scheduled"),
                "last_polled_ts": now_ts,
            }

            # Only add flights that have a flight_iata so keys are well-formed.
            if compact["flight_iata"]:
                flights.append(compact)

        return flights
