import json
import sqlite3
from datetime import datetime
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


def save_user_preferences(
    telegram_user_id: int,
    city: str,
    job_type: str,
    schedule: str,
) -> None:
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO user_preferences (
                telegram_user_id,
                city,
                job_type,
                schedule,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                city = excluded.city,
                job_type = excluded.job_type,
                schedule = excluded.schedule,
                updated_at = excluded.updated_at
            """,
            (
                telegram_user_id,
                city,
                job_type,
                schedule,
                now,
            ),
        )
        conn.commit()


def get_user_preferences(telegram_user_id: int) -> tuple | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT city, job_type, schedule, updated_at
            FROM user_preferences
            WHERE telegram_user_id = ?
            """,
            (telegram_user_id,),
        ).fetchone()

    return row


def set_user_subscription(telegram_user_id: int, is_subscribed: bool) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users
            SET is_subscribed_to_updates = ?
            WHERE telegram_user_id = ?
            """,
            (1 if is_subscribed else 0, telegram_user_id),
        )
        conn.commit()


def upsert_user(
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> None:
    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (
                telegram_user_id,
                username,
                first_name,
                last_name,
                first_seen_at,
                last_seen_at,
                is_subscribed_to_updates
            )
            VALUES (?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                last_seen_at = excluded.last_seen_at
            """,
            (
                telegram_user_id,
                username,
                first_name,
                last_name,
                now,
                now,
            ),
        )
        conn.commit()


def get_matching_subscribed_users(city: str, job_type: str, schedule: str):
    with get_connection() as conn:
        query = """
            SELECT u.telegram_user_id, u.username
            FROM users u
            JOIN user_preferences p
              ON u.telegram_user_id = p.telegram_user_id
            WHERE u.is_subscribed_to_updates = 1
              AND p.job_type = ?
        """
        params = [job_type]

        if city != "all":
            query += " AND p.city = ?"
            params.append(city)

        if schedule == "Гибкий график":
            query += " AND p.schedule IN ('Гибкий график', 'Подработка')"
        else:
            query += " AND p.schedule = ?"
            params.append(schedule)

        rows = conn.execute(query, tuple(params)).fetchall()

    return rows


def save_outbound_notification(
    telegram_user_id: int,
    offer_id: int,
    status: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO outbound_notifications (
                telegram_user_id,
                offer_id,
                sent_at,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                telegram_user_id,
                offer_id,
                datetime.utcnow().isoformat(),
                status,
            ),
        )
        conn.commit()

def was_offer_sent(telegram_user_id: int, offer_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM outbound_notifications
            WHERE telegram_user_id = ?
              AND offer_id = ?
              AND status = 'sent'
            LIMIT 1
            """,
            (telegram_user_id, offer_id),
        ).fetchone()

    return row is not None