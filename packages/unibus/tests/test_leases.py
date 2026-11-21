"""
Tests for UniBus Work Mutex Leases.
"""

import time
import pytest
from pathlib import Path
from unibus.bus import UniBus


@pytest.fixture
def bus(tmp_path: Path) -> UniBus:
    db_file = tmp_path / "test_unibus.db"
    return UniBus(db_path=db_file)


def test_acquire_and_release_lease(bus: UniBus):
    ok, lease, reason = bus.acquire_lease(
        resource_id="file:src/auth.py",
        owner_agent="security_prime",
        ttl_seconds=30
    )
    assert ok is True
    assert lease is not None
    assert lease.owner_agent == "security_prime"
    assert not lease.is_expired()

    # Re-acquire by same owner should renew successfully
    ok2, lease2, reason2 = bus.acquire_lease(
        resource_id="file:src/auth.py",
        owner_agent="security_prime",
        ttl_seconds=60
    )
    assert ok2 is True

    # Release
    released = bus.release_lease("file:src/auth.py", owner_agent="security_prime")
    assert released is True

    # Check list
    leases = bus.list_leases(active_only=True)
    assert len(leases) == 0


def test_lease_collision_rejection(bus: UniBus):
    # Agent 1 locks resource
    ok1, _, _ = bus.acquire_lease(
        resource_id="module:database",
        owner_agent="agent_alpha",
        ttl_seconds=10
    )
    assert ok1 is True

    # Agent 2 attempts to lock same resource -> MUST FAIL
    ok2, existing_lease, reason = bus.acquire_lease(
        resource_id="module:database",
        owner_agent="agent_beta",
        ttl_seconds=10
    )
    assert ok2 is False
    assert "agent_alpha" in reason
    assert existing_lease.owner_agent == "agent_alpha"


def test_expired_lease_atomic_reclaim(bus: UniBus):
    # Lock with 1s TTL
    ok1, _, _ = bus.acquire_lease(
        resource_id="file:config.py",
        owner_agent="old_agent",
        ttl_seconds=1
    )
    assert ok1 is True

    # Wait for expiry
    time.sleep(1.2)

    # Agent 2 attempts to lock -> should succeed because lease expired
    ok2, new_lease, reason = bus.acquire_lease(
        resource_id="file:config.py",
        owner_agent="new_agent",
        ttl_seconds=30
    )
    assert ok2 is True
    assert new_lease.owner_agent == "new_agent"


def test_reap_expired_leases(bus: UniBus):
    bus.acquire_lease("res_1", "agent_1", ttl_seconds=1)
    bus.acquire_lease("res_2", "agent_2", ttl_seconds=60)

    time.sleep(1.2)
    evicted = bus.reap_expired_leases()
    assert evicted == 1

    remaining = bus.list_leases(active_only=False)
    assert len(remaining) == 1
    assert remaining[0].resource_id == "res_2"
