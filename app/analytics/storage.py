import json
import sqlite3
from pathlib import Path
from typing import Any
from datetime import datetime


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

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                is_subscribed_to_updates INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL UNIQUE,
                city TEXT,
                job_type TEXT,
                schedule TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_offer_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                offer_id INTEGER NOT NULL,
                interaction_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outbound_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                offer_id INTEGER NOT NULL,
                sent_at TEXT NOT NULL,
                status TEXT NOT NULL
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

def save_offer_interaction(
    telegram_user_id: int,
    offer_id: int,
    interaction_type: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO user_offer_interactions (
                telegram_user_id,
                offer_id,
                interaction_type,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                telegram_user_id,
                offer_id,
                interaction_type,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()