"""
UniMemory Tier 1: Working Context Memory
========================================
Turn-by-turn context paging and active working cache.
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from unimemory.db import get_db_connection
from unimemory.models import WorkingMemoryItem
from unimemory.config import WORKING_MEMORY_TTL_HOURS, MAX_WORKING_ITEMS


class WorkingMemoryManager:

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self._conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return get_db_connection()

    def set(
        self,
        key: str,
        value: Any,
        project_scope: str = "GLOBAL",
        priority: int = 1,
        ttl_hours: int = WORKING_MEMORY_TTL_HOURS
    ) -> WorkingMemoryItem:
        """Stores or updates a working context key-value item."""
        conn = self._get_conn()
        cur = conn.cursor()

        val_json = json.dumps(value) if not isinstance(value, str) else value
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(hours=ttl_hours)).isoformat()
        now_str = now.isoformat()

        cur.execute("""
            INSERT INTO working_context (key, value_json, project_scope, priority, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value_json = excluded.value_json,
                project_scope = excluded.project_scope,
                priority = excluded.priority,
                created_at = excluded.created_at,
                expires_at = excluded.expires_at;
        """, (key, val_json, project_scope, priority, now_str, expires))

        # Sync to FTS5
        cur.execute("DELETE FROM memory_fts WHERE doc_id = ? AND tier_name = 'working'", (key,))
        cur.execute("""
            INSERT INTO memory_fts (doc_id, tier_name, entity_key, content_text, project)
            VALUES (?, 'working', ?, ?, ?)
        """, (key, key, f"{key}: {val_json}", project_scope))

        conn.commit()

        return WorkingMemoryItem(
            key=key,
            value_json=val_json,
            project_scope=project_scope,
            priority=priority,
            created_at=now_str,
            expires_at=expires
        )

    def get(self, key: str) -> Optional[WorkingMemoryItem]:
        """Retrieves a single working context item if not expired."""
        conn = self._get_conn()
        cur = conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()

        cur.execute("""
            SELECT key, value_json, project_scope, priority, created_at, expires_at
            FROM working_context
            WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
        """, (key, now_str))

        row = cur.fetchone()
        if not row:
            return None

        return WorkingMemoryItem(
            key=row["key"],
            value_json=row["value_json"],
            project_scope=row["project_scope"],
            priority=row["priority"],
            created_at=str(row["created_at"]),
            expires_at=str(row["expires_at"]) if row["expires_at"] else None
        )

    def list_active(self, project_scope: Optional[str] = None, limit: int = MAX_WORKING_ITEMS) -> List[WorkingMemoryItem]:
        """Lists active unexpired working context items."""
        conn = self._get_conn()
        cur = conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()

        if project_scope and project_scope != "GLOBAL":
            cur.execute("""
                SELECT key, value_json, project_scope, priority, created_at, expires_at
                FROM working_context
                WHERE (project_scope = ? OR project_scope = 'GLOBAL')
                  AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY priority DESC, created_at DESC
                LIMIT ?
            """, (project_scope, now_str, limit))
        else:
            cur.execute("""
                SELECT key, value_json, project_scope, priority, created_at, expires_at
                FROM working_context
                WHERE (expires_at IS NULL OR expires_at > ?)
                ORDER BY priority DESC, created_at DESC
                LIMIT ?
            """, (now_str, limit))

        rows = cur.fetchall()
        return [
            WorkingMemoryItem(
                key=r["key"],
                value_json=r["value_json"],
                project_scope=r["project_scope"],
                priority=r["priority"],
                created_at=str(r["created_at"]),
                expires_at=str(r["expires_at"]) if r["expires_at"] else None
            )
            for r in rows
        ]

    def prune_expired(self) -> int:
        """Removes expired working context records and cleans FTS5 index."""
        conn = self._get_conn()
        cur = conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()

        cur.execute("SELECT key FROM working_context WHERE expires_at IS NOT NULL AND expires_at <= ?", (now_str,))
        expired_keys = [r["key"] for r in cur.fetchall()]

        if not expired_keys:
            return 0

        cur.execute("DELETE FROM working_context WHERE expires_at IS NOT NULL AND expires_at <= ?", (now_str,))
        for k in expired_keys:
            cur.execute("DELETE FROM memory_fts WHERE doc_id = ? AND tier_name = 'working'", (k,))

        conn.commit()
        return len(expired_keys)
