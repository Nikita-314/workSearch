from datetime import datetime
from typing import Any


def log_event(event_name: str, user_id: int, **payload: Any) -> None:
    timestamp = datetime.utcnow().isoformat()

    print(
        {
            "timestamp": timestamp,
            "event": event_name,
            "user_id": user_id,
            "payload": payload,
        }
    )