"""
UniBus Data Models & Schemas (Pydantic v2).
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class EventPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

    @property
    def rank(self) -> int:
        ranks = {
            "CRITICAL": 1,
            "HIGH": 2,
            "NORMAL": 3,
            "LOW": 4,
        }
        return ranks.get(self.value, 3)


class EventStatus(str, Enum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class DecisionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    SUPERSEDED = "SUPERSEDED"
    REVOKED = "REVOKED"


class AgentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    TERMINATED = "TERMINATED"
    STALE = "STALE"


def get_current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConstraintRecord(BaseModel):
    constraint_key: str = Field(..., description="Unique constraint identifier (e.g. MAX_TOKEN_LIMIT)")
    domain: str = Field("GENERAL", description="Architectural domain (SECURITY, DATABASE, UI, etc.)")
    value_json: str = Field(..., description="JSON serialized constraint value")
    unit: Optional[str] = Field(None, description="Physical/operational unit (seconds, bytes, count, etc.)")
    rationale: Optional[str] = Field(None, description="Reason or invariant behind the constraint")
    imposing_agent: str = Field("system", description="Agent that established this constraint")
    version: int = Field(1, description="Constraint version number")
    updated_at: str = Field(default_factory=get_current_utc_iso)

    def get_parsed_value(self) -> Any:
        import json
        try:
            return json.loads(self.value_json)
        except Exception:
            return self.value_json


class DecisionRecord(BaseModel):
    decision_id: str = Field(..., description="Unique ADR ID (e.g. adr_001)")
    title: str = Field(..., description="Brief architectural decision title")
    status: DecisionStatus = Field(DecisionStatus.ACCEPTED, description="Lifecycle status")
    decision_text: str = Field("", description="Detailed architectural choice made")
    rationale: str = Field("", description="Justification and trade-offs considered")
    consequences: str = Field("", description="Expected impact, downstream effects")
    author_agent: str = Field("system", description="Agent that authored the decision")
    superseded_by: Optional[str] = Field(None, description="New decision_id that replaces this")
    timestamp: str = Field(default_factory=get_current_utc_iso)


class WorkLeaseRecord(BaseModel):
    resource_id: str = Field(..., description="Unique resource being locked (e.g. file:src/auth.py)")
    owner_agent: str = Field(..., description="Agent claiming exclusive access")
    acquired_at: str = Field(default_factory=get_current_utc_iso)
    expires_at: str = Field(..., description="ISO expiration timestamp")
    ttl_seconds: int = Field(60, description="Lease duration in seconds")
    metadata_json: str = Field("{}", description="Optional JSON metadata")

    def is_expired(self) -> bool:
        try:
            exp_dt = datetime.fromisoformat(self.expires_at)
            now_dt = datetime.now(timezone.utc)
            return now_dt > exp_dt
        except Exception:
            return True


class EventRecord(BaseModel):
    event_id: str = Field(..., description="Unique event identifier (e.g. evt_abc123)")
    topic: str = Field(..., description="Event topic (e.g. security.alert, build.completed)")
    priority: EventPriority = Field(EventPriority.NORMAL, description="Event urgency")
    payload_json: str = Field("{}", description="Serialized event data")
    status: EventStatus = Field(EventStatus.PENDING, description="Lifecycle state")
    claimed_by: Optional[str] = Field(None, description="Agent currently processing this event")
    created_at: str = Field(default_factory=get_current_utc_iso)
    resolved_at: Optional[str] = Field(None, description="Timestamp when event was resolved")

    def get_payload(self) -> Dict[str, Any]:
        import json
        try:
            return json.loads(self.payload_json)
        except Exception:
            return {"raw": self.payload_json}


class AgentHeartbeatRecord(BaseModel):
    agent_name: str = Field(..., description="Unique agent identifier or prime name")
    status: AgentStatus = Field(AgentStatus.ACTIVE, description="Current operational state")
    current_task: Optional[str] = Field(None, description="Active task being executed")
    last_seen: str = Field(default_factory=get_current_utc_iso)
    metadata_json: str = Field("{}", description="Additional status telemetry")

    def is_stale(self, threshold_seconds: int = 60) -> bool:
        try:
            seen_dt = datetime.fromisoformat(self.last_seen)
            now_dt = datetime.now(timezone.utc)
            return (now_dt - seen_dt).total_seconds() > threshold_seconds
        except Exception:
            return True
