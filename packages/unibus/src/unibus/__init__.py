"""
UniBus: Sovereign Real-Time Unix Domain Socket IPC & Shared Bus State Subsystem.
"""

from unibus.models import (
    EventPriority,
    EventStatus,
    DecisionStatus,
    AgentStatus,
    ConstraintRecord,
    DecisionRecord,
    WorkLeaseRecord,
    EventRecord,
    AgentHeartbeatRecord,
)
from unibus.bus import UniBus
from unibus.engine import UniBusEngine
from unibus.uds import UDSServer, publish_uds_sync, is_uds_server_alive

__version__ = "2026.1.0"
__all__ = [
    "UniBus",
    "UniBusEngine",
    "UDSServer",
    "publish_uds_sync",
    "is_uds_server_alive",
    "EventPriority",
    "EventStatus",
    "DecisionStatus",
    "AgentStatus",
    "ConstraintRecord",
    "DecisionRecord",
    "WorkLeaseRecord",
    "EventRecord",
    "AgentHeartbeatRecord",
]
