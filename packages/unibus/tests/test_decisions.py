"""
Tests for UniBus Architectural Decisions (ADR Ledger).
"""

import pytest
from pathlib import Path
from unibus.bus import UniBus
from unibus.models import DecisionStatus


@pytest.fixture
def bus(tmp_path: Path) -> UniBus:
    db_file = tmp_path / "test_unibus.db"
    return UniBus(db_path=db_file)


def test_log_decision(bus: UniBus):
    dec = bus.log_decision(
        title="Zero-Suppress Invariant Enforcement",
        decision_text="All @Suppress annotations strictly rejected in AST linting",
        rationale="Law-000 zero-shortcut invariant",
        consequences="Build will fail if any suppression is introduced",
        author_agent="univerify"
    )
    assert dec.decision_id.startswith("adr_")
    assert dec.status == DecisionStatus.ACCEPTED
    assert dec.title == "Zero-Suppress Invariant Enforcement"

    listed = bus.list_decisions(status=DecisionStatus.ACCEPTED)
    assert len(listed) == 1
    assert listed[0].decision_id == dec.decision_id


def test_supersede_decision(bus: UniBus):
    dec1 = bus.log_decision(title="V1 Memory Buffer", decision_id="adr_mem_v1")
    dec2 = bus.log_decision(title="V2 Memory Buffer", decision_id="adr_mem_v2")

    superseded = bus.supersede_decision("adr_mem_v1", "adr_mem_v2")
    assert superseded is True

    accepted = bus.list_decisions(status=DecisionStatus.ACCEPTED)
    assert len(accepted) == 1
    assert accepted[0].decision_id == "adr_mem_v2"

    superseded_list = bus.list_decisions(status=DecisionStatus.SUPERSEDED)
    assert len(superseded_list) == 1
    assert superseded_list[0].superseded_by == "adr_mem_v2"


def test_revoke_decision(bus: UniBus):
    dec = bus.log_decision(title="Experimental Cache", decision_id="adr_cache_exp")
    revoked = bus.revoke_decision("adr_cache_exp", rationale="Found memory leak")
    assert revoked is True

    revoked_list = bus.list_decisions(status=DecisionStatus.REVOKED)
    assert len(revoked_list) == 1
    assert "Found memory leak" in revoked_list[0].rationale
