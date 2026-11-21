"""
UniBus SQLite WAL Database Persistence Layer.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from unibus.config import CANONICAL_DB_PATH


SCHEMA_SQL = """
-- 1. Architectural Constraints Tuple Space
CREATE TABLE IF NOT EXISTS architectural_constraints (
    constraint_key TEXT PRIMARY KEY,
    domain TEXT NOT NULL DEFAULT 'GENERAL',
    value_json TEXT NOT NULL,
    unit TEXT,
    rationale TEXT,
    imposing_agent TEXT NOT NULL DEFAULT 'system',
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_constraints_domain ON architectural_constraints(domain);

-- 2. Architectural Decision Records (ADRs)
CREATE TABLE IF NOT EXISTS architectural_decisions (
    decision_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACCEPTED',
    decision_text TEXT NOT NULL DEFAULT '',
    rationale TEXT NOT NULL DEFAULT '',
    consequences TEXT NOT NULL DEFAULT '',
    author_agent TEXT NOT NULL DEFAULT 'system',
    superseded_by TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON architectural_decisions(status);

-- 3. Work Item Leases (Atomic Mutex Locks)
CREATE TABLE IF NOT EXISTS work_leases (
    resource_id TEXT PRIMARY KEY,
    owner_agent TEXT NOT NULL,
    acquired_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    ttl_seconds INTEGER NOT NULL DEFAULT 60,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_leases_expires ON work_leases(expires_at);

-- 4. Bus Priority Event Queue
CREATE TABLE IF NOT EXISTS bus_events (
    event_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'NORMAL',
    payload_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'PENDING',
    claimed_by TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_status_priority ON bus_events(status, priority, created_at);
CREATE INDEX IF NOT EXISTS idx_events_topic ON bus_events(topic);

-- 5. Agent Heartbeats & Telemetry
CREATE TABLE IF NOT EXISTS agent_heartbeats (
    agent_name TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    current_task TEXT,
    last_seen TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
"""


class DatabaseManager:
    """Manages SQLite WAL connection and transactions with fail-safe concurrency."""

    def __init__(self, db_path: Path = CANONICAL_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            isolation_level=None
        )
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self.get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE;")
            yield conn
            conn.execute("COMMIT;")
        except Exception:
            conn.execute("ROLLBACK;")
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
