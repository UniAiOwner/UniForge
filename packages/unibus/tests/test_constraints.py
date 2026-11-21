"""
Tests for UniBus Architectural Constraints Tuple Space.
"""

import pytest
from pathlib import Path
from unibus.bus import UniBus


@pytest.fixture
def bus(tmp_path: Path) -> UniBus:
    db_file = tmp_path / "test_unibus.db"
    return UniBus(db_path=db_file)


def test_set_and_get_constraint(bus: UniBus):
    rec = bus.set_constraint(
        key="MAX_AUTH_TOKEN_TTL_SEC",
        value=900,
        domain="SECURITY",
        unit="seconds",
        rationale="Argon2id + 15m JWT invariant",
        imposing_agent="auth_guardian"
    )
    assert rec.constraint_key == "MAX_AUTH_TOKEN_TTL_SEC"
    assert rec.domain == "SECURITY"
    assert rec.get_parsed_value() == 900
    assert rec.version == 1

    fetched = bus.get_constraint("MAX_AUTH_TOKEN_TTL_SEC")
    assert fetched is not None
    assert fetched.get_parsed_value() == 900
    assert fetched.imposing_agent == "auth_guardian"


def test_constraint_version_increment(bus: UniBus):
    bus.set_constraint("RATE_LIMIT", 100, domain="PERFORMANCE")
    rec2 = bus.set_constraint("RATE_LIMIT", 200, domain="PERFORMANCE")
    assert rec2.version == 2
    assert rec2.get_parsed_value() == 200


def test_list_constraints_by_domain(bus: UniBus):
    bus.set_constraint("DB_POOL_SIZE", 20, domain="DATABASE")
    bus.set_constraint("DB_TIMEOUT", 5, domain="DATABASE")
    bus.set_constraint("MAX_FPS", 60, domain="UI")

    db_items = bus.list_constraints(domain="DATABASE")
    assert len(db_items) == 2
    keys = {c.constraint_key for c in db_items}
    assert keys == {"DB_POOL_SIZE", "DB_TIMEOUT"}

    all_items = bus.list_constraints()
    assert len(all_items) == 3
