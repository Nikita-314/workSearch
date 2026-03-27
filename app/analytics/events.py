from datetime import datetime
from typing import Any

from app.analytics.storage import save_event


def log_event(event_name: str, user_id: int, **payload: Any) -> None:
    timestamp = datetime.utcnow().isoformat()

    event_data = {
        "timestamp": timestamp,
        "event": event_name,
        "user_id": user_id,
        "payload": payload,
    }

    print(event_data)
    save_event(
        timestamp=timestamp,
        event_name=event_name,
        user_id=user_id,
        payload=payload,
    )