"""
UniBus Core Engine.
Single source of truth for:
1. Real-Time Unix Domain Socket (UDS) IPC (< 0.1ms)
2. Distributed Work Mutex Leases (File/Task collision protection)
3. Priority Event Pub/Sub
4. Architectural Constraints Tuple Space
5. Architectural Decision Records (ADRs)
6. Agent Heartbeat & Liveness
"""

import json
import uuid
from typing import List, Optional, Any, Dict, Tuple
from datetime import datetime, timezone, timedelta
from pathlib import Path

from unibus.config import (
    CANONICAL_DB_PATH,
    CANONICAL_SOCKET_PATH,
    DEFAULT_LEASE_TTL_SECONDS,
    STALE_HEARTBEAT_THRESHOLD_SECONDS,
)
from unibus.db import DatabaseManager
from unibus.uds import is_uds_server_alive, publish_uds_sync
from unibus.models import (
    ConstraintRecord,
    DecisionRecord,
    DecisionStatus,
    WorkLeaseRecord,
    EventRecord,
    EventPriority,
    EventStatus,
    AgentHeartbeatRecord,
    AgentStatus,
    get_current_utc_iso,
)


class UniBus:
    """Unified UniBus Engine coordinating real-time IPC and persistent shared state."""

    def __init__(
        self,
        db_path: Path = CANONICAL_DB_PATH,
        socket_path: Path = CANONICAL_SOCKET_PATH
    ):
        self.db_path = Path(db_path)
        self.socket_path = Path(socket_path)
        self.db = DatabaseManager(self.db_path)

    # ==========================================
    # 1. Architectural Constraints
    # ==========================================

    def set_constraint(
        self,
        key: str,
        value: Any,
        domain: str = "GENERAL",
        unit: Optional[str] = None,
        rationale: Optional[str] = None,
        imposing_agent: str = "system"
    ) -> ConstraintRecord:
        val_json = json.dumps(value) if not isinstance(value, str) else value
        now_iso = get_current_utc_iso()

        with self.db.transaction() as conn:
            row = conn.execute(
                "SELECT version FROM architectural_constraints WHERE constraint_key = ?",
                (key,)
            ).fetchone()
            new_version = (row["version"] + 1) if row else 1

            conn.execute(
                """
                INSERT INTO architectural_constraints 
                (constraint_key, domain, value_json, unit, rationale, imposing_agent, version, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(constraint_key) DO UPDATE SET
                    domain = excluded.domain,
                    value_json = excluded.value_json,
                    unit = excluded.unit,
                    rationale = excluded.rationale,
                    imposing_agent = excluded.imposing_agent,
                    version = excluded.version,
                    updated_at = excluded.updated_at
                """,
                (key, domain.upper(), val_json, unit, rationale, imposing_agent, new_version, now_iso)
            )

        return ConstraintRecord(
            constraint_key=key,
            domain=domain.upper(),
            value_json=val_json,
            unit=unit,
            rationale=rationale,
            imposing_agent=imposing_agent,
            version=new_version,
            updated_at=now_iso
        )

    def get_constraint(self, key: str, domain: Optional[str] = None) -> Optional[ConstraintRecord]:
        query = "SELECT * FROM architectural_constraints WHERE constraint_key = ?"
        params = [key]
        if domain:
            query += " AND domain = ?"
            params.append(domain.upper())

        conn = self.db.get_connection()
        try:
            row = conn.execute(query, params).fetchone()
            if not row:
                return None
            return ConstraintRecord(**dict(row))
        finally:
            conn.close()

    def list_constraints(self, domain: Optional[str] = None) -> List[ConstraintRecord]:
        query = "SELECT * FROM architectural_constraints"
        params = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain.upper())
        query += " ORDER BY domain ASC, constraint_key ASC"

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [ConstraintRecord(**dict(r)) for r in rows]
        finally:
            conn.close()

    # ==========================================
    # 2. Architectural Decisions (ADR)
    # ==========================================

    def log_decision(
        self,
        title: str,
        decision_text: str = "",
        rationale: str = "",
        consequences: str = "",
        author_agent: str = "system",
        status: DecisionStatus = DecisionStatus.ACCEPTED,
        decision_id: Optional[str] = None
    ) -> DecisionRecord:
        did = decision_id or f"adr_{uuid.uuid4().hex[:8]}"
        now_iso = get_current_utc_iso()

        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO architectural_decisions
                (decision_id, title, status, decision_text, rationale, consequences, author_agent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET
                    title = excluded.title,
                    status = excluded.status,
                    decision_text = excluded.decision_text,
                    rationale = excluded.rationale,
                    consequences = excluded.consequences,
                    author_agent = excluded.author_agent,
                    timestamp = excluded.timestamp
                """,
                (did, title, status.value, decision_text, rationale, consequences, author_agent, now_iso)
            )

        return DecisionRecord(
            decision_id=did,
            title=title,
            status=status,
            decision_text=decision_text,
            rationale=rationale,
            consequences=consequences,
            author_agent=author_agent,
            timestamp=now_iso
        )

    def list_decisions(self, status: Optional[DecisionStatus] = None) -> List[DecisionRecord]:
        query = "SELECT * FROM architectural_decisions"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        query += " ORDER BY timestamp DESC"

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [DecisionRecord(**dict(r)) for r in rows]
        finally:
            conn.close()

    def supersede_decision(self, old_id: str, new_id: str) -> bool:
        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE architectural_decisions 
                SET status = 'SUPERSEDED', superseded_by = ? 
                WHERE decision_id = ?
                """,
                (new_id, old_id)
            )
            return cursor.rowcount > 0

    def revoke_decision(self, decision_id: str, rationale: str = "") -> bool:
        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE architectural_decisions 
                SET status = 'REVOKED', rationale = CASE WHEN ? != '' THEN rationale || ' [REVOKED: ' || ? || ']' ELSE rationale END
                WHERE decision_id = ?
                """,
                (rationale, rationale, decision_id)
            )
            return cursor.rowcount > 0

    # ==========================================
    # 3. Distributed Work Leases (Atomic Mutex)
    # ==========================================

    def acquire_lease(
        self,
        resource_id: str,
        owner_agent: str,
        ttl_seconds: int = DEFAULT_LEASE_TTL_SECONDS,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[WorkLeaseRecord], str]:
        meta_json = json.dumps(metadata or {})
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        exp_dt = now_dt + timedelta(seconds=ttl_seconds)
        exp_iso = exp_dt.isoformat()

        with self.db.transaction() as conn:
            existing = conn.execute(
                "SELECT * FROM work_leases WHERE resource_id = ?",
                (resource_id,)
            ).fetchone()

            if existing:
                cur_owner = existing["owner_agent"]
                cur_exp_str = existing["expires_at"]
                try:
                    cur_exp_dt = datetime.fromisoformat(cur_exp_str)
                    is_active = now_dt <= cur_exp_dt
                except Exception:
                    is_active = False

                if is_active and cur_owner != owner_agent:
                    remaining = (cur_exp_dt - now_dt).total_seconds()
                    rec = WorkLeaseRecord(**dict(existing))
                    return False, rec, f"Resource locked by '{cur_owner}' for another {remaining:.1f}s"

            conn.execute(
                """
                INSERT INTO work_leases (resource_id, owner_agent, acquired_at, expires_at, ttl_seconds, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(resource_id) DO UPDATE SET
                    owner_agent = excluded.owner_agent,
                    acquired_at = excluded.acquired_at,
                    expires_at = excluded.expires_at,
                    ttl_seconds = excluded.ttl_seconds,
                    metadata_json = excluded.metadata_json
                """,
                (resource_id, owner_agent, now_iso, exp_iso, ttl_seconds, meta_json)
            )

        new_rec = WorkLeaseRecord(
            resource_id=resource_id,
            owner_agent=owner_agent,
            acquired_at=now_iso,
            expires_at=exp_iso,
            ttl_seconds=ttl_seconds,
            metadata_json=meta_json
        )
        return True, new_rec, "Lease acquired successfully"

    def release_lease(self, resource_id: str, owner_agent: Optional[str] = None) -> bool:
        with self.db.transaction() as conn:
            query = "DELETE FROM work_leases WHERE resource_id = ?"
            params = [resource_id]
            if owner_agent:
                query += " AND owner_agent = ?"
                params.append(owner_agent)
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

    def list_leases(self, active_only: bool = True) -> List[WorkLeaseRecord]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute("SELECT * FROM work_leases ORDER BY acquired_at DESC").fetchall()
            leases = [WorkLeaseRecord(**dict(r)) for r in rows]
            if active_only:
                leases = [l for l in leases if not l.is_expired()]
            return leases
        finally:
            conn.close()

    def reap_expired_leases(self) -> int:
        now_iso = get_current_utc_iso()
        with self.db.transaction() as conn:
            cursor = conn.execute("DELETE FROM work_leases WHERE expires_at < ?", (now_iso,))
            return cursor.rowcount

    # ==========================================
    # 4. Priority Event Queue & Real-Time Broadcast
    # ==========================================

    def publish_event(
        self,
        topic: str,
        payload: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        event_id: Optional[str] = None
    ) -> EventRecord:
        eid = event_id or f"evt_{uuid.uuid4().hex[:12]}"
        now_iso = get_current_utc_iso()
        payload_json = json.dumps(payload)

        # 1. Persist to WAL DB
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO bus_events
                (event_id, topic, priority, payload_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (eid, topic, priority.value, payload_json, EventStatus.PENDING.value, now_iso)
            )

        event_rec = EventRecord(
            event_id=eid,
            topic=topic,
            priority=priority,
            payload_json=payload_json,
            status=EventStatus.PENDING,
            created_at=now_iso
        )

        # 2. Fast-path UDS socket broadcast (sub-0.1ms) if daemon is running
        publish_uds_sync(event_rec.model_dump(), socket_path=self.socket_path)

        return event_rec

    def poll_events(
        self,
        topic: Optional[str] = None,
        priority: Optional[EventPriority] = None,
        status: EventStatus = EventStatus.PENDING,
        limit: int = 50
    ) -> List[EventRecord]:
        query = "SELECT * FROM bus_events WHERE status = ?"
        params: List[Any] = [status.value]

        if topic:
            if "*" in topic:
                pattern = topic.replace("*", "%")
                query += " AND topic LIKE ?"
                params.append(pattern)
            else:
                query += " AND topic = ?"
                params.append(topic)

        if priority:
            query += " AND priority = ?"
            params.append(priority.value)

        query += """
            ORDER BY CASE priority
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'NORMAL' THEN 3
                WHEN 'LOW' THEN 4
                ELSE 5
            END ASC, created_at ASC LIMIT ?
        """
        params.append(limit)

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [EventRecord(**dict(r)) for r in rows]
        finally:
            conn.close()

    def claim_event(self, event_id: str, agent_name: str) -> bool:
        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE bus_events 
                SET status = 'CLAIMED', claimed_by = ? 
                WHERE event_id = ? AND status = 'PENDING'
                """,
                (agent_name, event_id)
            )
            return cursor.rowcount > 0

    def resolve_event(self, event_id: str) -> bool:
        now_iso = get_current_utc_iso()
        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE bus_events 
                SET status = 'RESOLVED', resolved_at = ? 
                WHERE event_id = ? AND status IN ('PENDING', 'CLAIMED')
                """,
                (now_iso, event_id)
            )
            return cursor.rowcount > 0

    # ==========================================
    # 5. Agent Heartbeats & Telemetry
    # ==========================================

    def record_heartbeat(
        self,
        agent_name: str,
        status: AgentStatus = AgentStatus.ACTIVE,
        current_task: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentHeartbeatRecord:
        now_iso = get_current_utc_iso()
        meta_json = json.dumps(metadata or {})

        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO agent_heartbeats (agent_name, status, current_task, last_seen, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(agent_name) DO UPDATE SET
                    status = excluded.status,
                    current_task = excluded.current_task,
                    last_seen = excluded.last_seen,
                    metadata_json = excluded.metadata_json
                """,
                (agent_name, status.value, current_task, now_iso, meta_json)
            )

        return AgentHeartbeatRecord(
            agent_name=agent_name,
            status=status,
            current_task=current_task,
            last_seen=now_iso,
            metadata_json=meta_json
        )

    def list_agents(self, active_only: bool = False) -> List[AgentHeartbeatRecord]:
        conn = self.db.get_connection()
        try:
            rows = conn.execute("SELECT * FROM agent_heartbeats ORDER BY last_seen DESC").fetchall()
            records = [AgentHeartbeatRecord(**dict(r)) for r in rows]
            if active_only:
                records = [r for r in records if not r.is_stale(STALE_HEARTBEAT_THRESHOLD_SECONDS)]
            return records
        finally:
            conn.close()

    def reap_stale_agents(self, threshold_seconds: int = STALE_HEARTBEAT_THRESHOLD_SECONDS) -> int:
        now_dt = datetime.now(timezone.utc)
        cutoff_iso = (now_dt - timedelta(seconds=threshold_seconds)).isoformat()
        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE agent_heartbeats 
                SET status = 'STALE' 
                WHERE last_seen < ? AND status = 'ACTIVE'
                """,
                (cutoff_iso,)
            )
            return cursor.rowcount

    # ==========================================
    # 6. Diagnostics & Status
    # ==========================================

    def doctor(self) -> Dict[str, Any]:
        db_exists = self.db_path.exists()
        db_writable = False
        if db_exists:
            try:
                with self.db.get_connection() as conn:
                    conn.execute("SELECT 1")
                db_writable = True
            except Exception:
                db_writable = False

        uds_alive = is_uds_server_alive(self.socket_path)
        active_leases = len(self.list_leases(active_only=True))
        stale_reaped = self.reap_expired_leases()
        constraints_count = len(self.list_constraints())
        decisions_count = len(self.list_decisions())
        pending_events = len(self.poll_events(limit=100))

        return {
            "status": "HEALTHY" if (db_exists and db_writable) else "DEGRADED",
            "db_path": str(self.db_path),
            "db_exists": db_exists,
            "db_writable": db_writable,
            "socket_path": str(self.socket_path),
            "socket_daemon_active": uds_alive,
            "constraints_count": constraints_count,
            "decisions_count": decisions_count,
            "active_leases": active_leases,
            "expired_leases_reaped": stale_reaped,
            "pending_events_count": pending_events,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "constraints": len(self.list_constraints()),
            "decisions": len(self.list_decisions()),
            "active_leases": len(self.list_leases(active_only=True)),
            "pending_events": len(self.poll_events(limit=500)),
            "active_agents": len(self.list_agents(active_only=True)),
            "socket_active": is_uds_server_alive(self.socket_path),
        }
