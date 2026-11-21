"""
UniMemory Cognitive Light Beacon Manager
========================================
Sovereign Living Mission Anchor & Anti-Drift Trajectory Sentinel.
Pins root mission and active milestones in an immutable database table,
injects ambient turn headers (< 35 tokens), and blocks out-of-scope actions.
"""

import json
import uuid
import fnmatch
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from unimemory.db import get_db_connection
from unimemory.models import CognitiveBeacon, BeaconDriftCheckResult


class BeaconManager:
    """
    Manages the lifecycle of Living Cognitive Beacons.
    Enforces the single-active-beacon invariant and validates action alignment.
    """

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None, db_path: Optional[Path] = None):
        self._conn = db_conn
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return get_db_connection(self.db_path)

    def set_active_beacon(
        self,
        mission_name: str,
        parent_goal: str,
        active_milestone: str,
        in_scope_paths: List[str],
        forbidden_domains: List[str]
    ) -> CognitiveBeacon:
        """
        Activates a new Cognitive Beacon.
        Automatically marks any previously active beacon as 'COMPLETED'.
        """
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        beacon_id = f"beacon-{uuid.uuid4().hex[:12]}"

        # Close any existing active beacon
        cur.execute(
            "UPDATE cognitive_beacons SET status = 'COMPLETED', updated_at = ? WHERE status = 'ACTIVE'",
            (now,)
        )

        cur.execute("""
            INSERT INTO cognitive_beacons (
                beacon_id, mission_name, parent_goal, active_milestone,
                in_scope_paths_json, forbidden_domains_json, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
        """, (
            beacon_id,
            mission_name,
            parent_goal,
            active_milestone,
            json.dumps(in_scope_paths),
            json.dumps(forbidden_domains),
            now,
            now
        ))

        conn.commit()

        return CognitiveBeacon(
            id=beacon_id,
            mission_name=mission_name,
            parent_goal=parent_goal,
            active_milestone=active_milestone,
            in_scope_paths=in_scope_paths,
            forbidden_domains=forbidden_domains,
            status="ACTIVE",
            created_at=now,
            updated_at=now
        )

    def get_active_beacon(self) -> Optional[CognitiveBeacon]:
        """Fetches the currently active living beacon in sub-millisecond time."""
        conn = self._get_conn()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT * FROM cognitive_beacons WHERE status = 'ACTIVE' LIMIT 1"
        ).fetchone()

        if not row:
            return None

        return CognitiveBeacon(
            id=row["beacon_id"],
            mission_name=row["mission_name"],
            parent_goal=row["parent_goal"],
            active_milestone=row["active_milestone"],
            in_scope_paths=json.loads(row["in_scope_paths_json"]),
            forbidden_domains=json.loads(row["forbidden_domains_json"]),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def check_drift(
        self,
        target_path: Optional[str] = None,
        intent_summary: str = ""
    ) -> BeaconDriftCheckResult:
        """
        Validates whether a proposed file path or action intent aligns with the active beacon.
        Fails closed if actions violate scope or contain forbidden domain keywords.
        """
        beacon = self.get_active_beacon()
        if not beacon:
            return BeaconDriftCheckResult(allowed=True, beacon_id=None)

        intent_lower = intent_summary.lower()

        # Check forbidden domain keywords
        for forbidden in beacon.forbidden_domains:
            forbidden_clean = forbidden.lower().strip()
            if not forbidden_clean:
                continue
            if forbidden_clean in intent_lower:
                return BeaconDriftCheckResult(
                    allowed=False,
                    beacon_id=beacon.id,
                    violation_reason=f"Action intent references forbidden domain keyword: '{forbidden}'. Active mission is locked to: '{beacon.mission_name}'."
                )
            if target_path and forbidden_clean in target_path.lower():
                return BeaconDriftCheckResult(
                    allowed=False,
                    beacon_id=beacon.id,
                    violation_reason=f"Target path '{target_path}' contains forbidden domain keyword: '{forbidden}'."
                )

        # Check in-scope file paths
        if target_path and beacon.in_scope_paths:
            normalized = target_path.replace("\\", "/")
            matched = False
            for pattern in beacon.in_scope_paths:
                pattern_clean = pattern.replace("\\", "/")
                if fnmatch.fnmatch(normalized, pattern_clean) or pattern_clean in normalized or fnmatch.fnmatch(Path(normalized).name, pattern_clean):
                    matched = True
                    break

            if not matched:
                return BeaconDriftCheckResult(
                    allowed=False,
                    beacon_id=beacon.id,
                    violation_reason=f"Target file '{target_path}' is outside allowed in-scope boundaries for active milestone '{beacon.active_milestone}'."
                )

        return BeaconDriftCheckResult(allowed=True, beacon_id=beacon.id)

    def complete_beacon(self, beacon_id: Optional[str] = None) -> bool:
        """Marks the active or specified beacon as COMPLETED."""
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        if beacon_id:
            cur.execute(
                "UPDATE cognitive_beacons SET status = 'COMPLETED', updated_at = ? WHERE beacon_id = ?",
                (now, beacon_id)
            )
        else:
            cur.execute(
                "UPDATE cognitive_beacons SET status = 'COMPLETED', updated_at = ? WHERE status = 'ACTIVE'",
                (now,)
            )
        changed = cur.rowcount > 0
        conn.commit()
        return changed

    def revoke_beacon(self, beacon_id: Optional[str] = None) -> bool:
        """Revokes / cancels the active or specified beacon."""
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        if beacon_id:
            cur.execute(
                "UPDATE cognitive_beacons SET status = 'REVOKED', updated_at = ? WHERE beacon_id = ?",
                (now, beacon_id)
            )
        else:
            cur.execute(
                "UPDATE cognitive_beacons SET status = 'REVOKED', updated_at = ? WHERE status = 'ACTIVE'",
                (now,)
            )
        changed = cur.rowcount > 0
        conn.commit()
        return changed

    def format_beacon_header(self) -> str:
        """Generates an ambient < 35 token header for instant turn awareness."""
        beacon = self.get_active_beacon()
        if not beacon:
            return "⬢ [NO ACTIVE BEACON: Run 'unimemory beacon set' to anchor mission]"
        return beacon.to_ambient_header()
