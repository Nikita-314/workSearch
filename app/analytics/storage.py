import json
import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "analytics.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_event(
    timestamp: str,
    event_name: str,
    user_id: int,
    payload: dict[str, Any],
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO events (timestamp, event_name, user_id, payload)
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                event_name,
                user_id,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        conn.commit()