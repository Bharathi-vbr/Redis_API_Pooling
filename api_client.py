import time
from typing import Dict, Any

import requests

from config import API_BASE_URL, TODO_ID


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def fetch_todo(self, todo_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/todos/{todo_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "completed": data.get("completed"),
            "userId": data.get("userId"),
            "last_polled_ts": int(time.time()),
        }
