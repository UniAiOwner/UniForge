"""
UniMemory Tier 2: Episodic Memory & Failure Reflections (Law-STARK)
===================================================================
Enforces the Tony Stark gold-titanium philosophy: record every crash,
distill the atmospheric icing countermeasure, and block repeat failures.
"""

import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from unimemory.db import get_db_connection
from unimemory.models import EpisodicEntry


class EpisodicMemoryManager:

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self._conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return get_db_connection()

    def record_episode(
        self,
        project: str,
        goal: str,
        steps_taken: List[str],
        errors_encountered: List[str],
        root_cause_lesson: str,
        status: str = "SUCCESS",
        episode_id: Optional[str] = None
    ) -> EpisodicEntry:
        """Records an episodic execution trace into the ledger."""
        conn = self._get_conn()
        cur = conn.cursor()

        now_str = datetime.now(timezone.utc).isoformat()
        if not episode_id:
            raw_hash = f"{project}:{goal}:{now_str}"
            episode_id = f"ep_{hashlib.sha256(raw_hash.encode()).hexdigest()[:12]}"

        steps_json = json.dumps(steps_taken)
        errors_json = json.dumps(errors_encountered)

        cur.execute("""
            INSERT OR REPLACE INTO episodic_ledger (
                episode_id, project, goal, steps_json, errors_json, root_cause_lesson, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (episode_id, project, goal, steps_json, errors_json, root_cause_lesson, status, now_str))

        # Sync to FTS5 index
        content_text = f"Goal: {goal} | Status: {status} | Lesson: {root_cause_lesson} | Errors: {' '.join(errors_encountered)}"
        cur.execute("DELETE FROM memory_fts WHERE doc_id = ? AND tier_name = 'episodic'", (episode_id,))
        cur.execute("""
            INSERT INTO memory_fts (doc_id, tier_name, entity_key, content_text, project)
            VALUES (?, 'episodic', ?, ?, ?)
        """, (episode_id, goal, content_text, project))

        conn.commit()

        return EpisodicEntry(
            episode_id=episode_id,
            project=project,
            goal=goal,
            steps_taken=steps_taken,
            errors_encountered=errors_encountered,
            root_cause_lesson=root_cause_lesson,
            status=status,
            created_at=now_str
        )

    def get_stark_countermeasures(self, task_or_goal: str, project: Optional[str] = None, limit: int = 3) -> List[EpisodicEntry]:
        """
        Retrieves relevant past failure lessons and countermeasures for the given task.
        Prevents repeating identical mistakes across turns or sessions.
        """
        conn = self._get_conn()
        cur = conn.cursor()

        clean_tokens = [t for t in task_or_goal.split() if len(t) > 2][:4]
        if not clean_tokens:
            return []

        fts_query = " OR ".join(f'"{t}"*' for t in clean_tokens)

        sql = """
            SELECT doc_id FROM memory_fts
            WHERE tier_name = 'episodic' AND memory_fts MATCH ?
        """
        params: List[Any] = [fts_query]
        if project:
            sql += " AND project = ?"
            params.append(project)

        sql += " LIMIT 15;"

        try:
            cur.execute(sql, params)
            doc_ids = [r["doc_id"] for r in cur.fetchall()]
        except Exception:
            return []

        if not doc_ids:
            return []

        placeholders = ",".join("?" for _ in doc_ids)
        cur.execute(f"""
            SELECT episode_id, project, goal, steps_json, errors_json, root_cause_lesson, status, created_at
            FROM episodic_ledger
            WHERE episode_id IN ({placeholders})
            ORDER BY CASE WHEN status != 'SUCCESS' THEN 0 ELSE 1 END, created_at DESC
            LIMIT ?
        """, (*doc_ids, limit))

        rows = cur.fetchall()
        entries = []
        for r in rows:
            entries.append(EpisodicEntry(
                episode_id=r["episode_id"],
                project=r["project"],
                goal=r["goal"],
                steps_taken=json.loads(r["steps_json"]),
                errors_encountered=json.loads(r["errors_json"]),
                root_cause_lesson=r["root_cause_lesson"],
                status=r["status"],
                created_at=str(r["created_at"])
            ))

        return entries

    def list_recent(self, project: Optional[str] = None, limit: int = 10) -> List[EpisodicEntry]:
        """Lists recent episodic execution logs."""
        conn = self._get_conn()
        cur = conn.cursor()

        if project:
            cur.execute("""
                SELECT episode_id, project, goal, steps_json, errors_json, root_cause_lesson, status, created_at
                FROM episodic_ledger
                WHERE project = ?
                ORDER BY created_at DESC LIMIT ?
            """, (project, limit))
        else:
            cur.execute("""
                SELECT episode_id, project, goal, steps_json, errors_json, root_cause_lesson, status, created_at
                FROM episodic_ledger
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))

        return [
            EpisodicEntry(
                episode_id=r["episode_id"],
                project=r["project"],
                goal=r["goal"],
                steps_taken=json.loads(r["steps_json"]),
                errors_encountered=json.loads(r["errors_json"]),
                root_cause_lesson=r["root_cause_lesson"],
                status=r["status"],
                created_at=str(r["created_at"])
            )
            for r in cur.fetchall()
        ]
