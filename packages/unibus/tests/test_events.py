"""
Tests for UniBus Priority Event Queue.
"""

import pytest
from pathlib import Path
from unibus.bus import UniBus
from unibus.models import EventPriority, EventStatus


@pytest.fixture
def bus(tmp_path: Path) -> UniBus:
    db_file = tmp_path / "test_unibus.db"
    return UniBus(db_path=db_file)


def test_event_priority_ordering(bus: UniBus):
    bus.publish_event("log.info", {"msg": "normal 1"}, priority=EventPriority.NORMAL)
    bus.publish_event("security.alert", {"msg": "critical leak"}, priority=EventPriority.CRITICAL)
    bus.publish_event("perf.warning", {"msg": "high latency"}, priority=EventPriority.HIGH)
    bus.publish_event("debug.trace", {"msg": "low trace"}, priority=EventPriority.LOW)

    polled = bus.poll_events(limit=10)
    assert len(polled) == 4
    priorities = [e.priority for e in polled]
    assert priorities == [
        EventPriority.CRITICAL,
        EventPriority.HIGH,
        EventPriority.NORMAL,
        EventPriority.LOW
    ]


def test_topic_wildcard_filtering(bus: UniBus):
    bus.publish_event("system.cpu.alert", {"load": 99})
    bus.publish_event("system.memory.alert", {"free_mb": 12})
    bus.publish_event("user.login", {"user": "admin"})

    system_events = bus.poll_events(topic="system.*")
    assert len(system_events) == 2
    for e in system_events:
        assert e.topic.startswith("system.")

    exact_events = bus.poll_events(topic="user.login")
    assert len(exact_events) == 1
    assert exact_events[0].topic == "user.login"


def test_claim_and_resolve_lifecycle(bus: UniBus):
    evt = bus.publish_event("task.ready", {"task_id": "t100"})
    assert evt.status == EventStatus.PENDING

    claimed = bus.claim_event(evt.event_id, "worker_prime")
    assert claimed is True

    claimed2 = bus.claim_event(evt.event_id, "worker_beta")
    assert claimed2 is False

    pending = bus.poll_events()
    assert len(pending) == 0

    resolved = bus.resolve_event(evt.event_id)
    assert resolved is True

    claimed_events = bus.poll_events(status=EventStatus.CLAIMED)
    assert len(claimed_events) == 0
