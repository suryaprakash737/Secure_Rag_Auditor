import sqlite3
import os
from datetime import datetime, timezone

_DB_PATH = os.path.join(os.path.dirname(__file__), "../audit.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL,
                query_text      TEXT    NOT NULL,
                user_clearance  INTEGER NOT NULL,
                risk_level      TEXT    NOT NULL,
                log_count       INTEGER NOT NULL,
                was_blocked     INTEGER NOT NULL
            )
        """)


_init_db()


def log_search(
    query_text: str,
    user_clearance: int,
    risk_level: str,
    log_count: int,
    was_blocked: bool,
) -> None:
    """Write one audit row. Opens and closes its own connection — safe for async/threaded use."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_log
                (timestamp, query_text, user_clearance, risk_level, log_count, was_blocked)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                query_text,
                user_clearance,
                risk_level,
                log_count,
                int(was_blocked),
            ),
        )
