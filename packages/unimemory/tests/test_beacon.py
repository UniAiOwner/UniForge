"""
Unit tests for UniMemory Cognitive Light Beacon Manager & Anti-Drift Sentinel
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from unimemory.engine import UniMemoryEngine
from unimemory.cli import app

runner = CliRunner()


@pytest.fixture
def test_engine(tmp_path):
    db_file = tmp_path / "test_beacon_memory.db"
    engine = UniMemoryEngine(db_path=db_file)
    return engine


def test_set_and_get_beacon(test_engine):
    b = test_engine.set_beacon(
        mission_name="UniCortex Brain 2.0",
        parent_goal="7-Pillar Sovereign Substrate",
        active_milestone="Pillar 5: UniExec",
        in_scope_paths=["Agentic team/**", "uniexec/**"],
        forbidden_domains=["retail", "khata", "billing"]
    )
    assert b.mission_name == "UniCortex Brain 2.0"
    assert b.active_milestone == "Pillar 5: UniExec"
    assert b.status == "ACTIVE"

    retrieved = test_engine.get_beacon()
    assert retrieved is not None
    assert retrieved.id == b.id
    assert retrieved.active_milestone == "Pillar 5: UniExec"
    assert "retail" in retrieved.forbidden_domains


def test_single_active_beacon_invariant(test_engine):
    b1 = test_engine.set_beacon(
        mission_name="Mission 1",
        parent_goal="Goal 1",
        active_milestone="Milestone 1",
        in_scope_paths=["path1/**"],
        forbidden_domains=[]
    )
    b2 = test_engine.set_beacon(
        mission_name="Mission 2",
        parent_goal="Goal 2",
        active_milestone="Milestone 2",
        in_scope_paths=["path2/**"],
        forbidden_domains=[]
    )

    active = test_engine.get_beacon()
    assert active.id == b2.id
    assert active.mission_name == "Mission 2"


def test_drift_check_allowed_in_scope(test_engine):
    test_engine.set_beacon(
        mission_name="UniCortex Brain 2.0",
        parent_goal="Build Substrate",
        active_milestone="Pillar 5: UniExec",
        in_scope_paths=["Agentic team/**", "uniexec/**"],
        forbidden_domains=["retail", "khata"]
    )

    res = test_engine.check_drift(
        target_path="Agentic team/uniexec/sandbox.py",
        intent_summary="Implement Bubblewrap container isolation"
    )
    assert res.allowed is True
    assert res.violation_reason is None


def test_drift_check_blocked_forbidden_domain_keyword(test_engine):
    test_engine.set_beacon(
        mission_name="UniCortex Brain 2.0",
        parent_goal="Build Substrate",
        active_milestone="Pillar 5: UniExec",
        in_scope_paths=["Agentic team/**"],
        forbidden_domains=["retail", "khata", "billing"]
    )

    res = test_engine.check_drift(
        target_path="Agentic team/test.py",
        intent_summary="Let us add khata ledger calculations here"
    )
    assert res.allowed is False
    assert "forbidden domain keyword: 'khata'" in res.violation_reason


def test_drift_check_blocked_out_of_scope_path(test_engine):
    test_engine.set_beacon(
        mission_name="UniCortex Brain 2.0",
        parent_goal="Build Substrate",
        active_milestone="Pillar 5: UniExec",
        in_scope_paths=["Agentic team/**", "uniexec/**"],
        forbidden_domains=[]
    )

    res = test_engine.check_drift(
        target_path="UniRetail/pos/BillingService.kt",
        intent_summary="Update invoice printer logic"
    )
    assert res.allowed is False
    assert "outside allowed in-scope boundaries" in res.violation_reason


def test_complete_beacon(test_engine):
    test_engine.set_beacon(
        mission_name="Mission Test",
        parent_goal="Goal Test",
        active_milestone="Milestone Test",
        in_scope_paths=[],
        forbidden_domains=[]
    )
    assert test_engine.get_beacon() is not None

    ok = test_engine.complete_beacon()
    assert ok is True
    assert test_engine.get_beacon() is None


def test_ambient_header_format(test_engine):
    b = test_engine.set_beacon(
        mission_name="UniCortex Brain 2.0",
        parent_goal="Substrate Rebirth",
        active_milestone="Pillar 5: UniExec",
        in_scope_paths=[],
        forbidden_domains=[]
    )
    header = b.to_ambient_header()
    assert "BEACON: UniCortex Brain 2.0" in header
    assert "ACTIVE: Pillar 5: UniExec" in header
    assert "LOCKED" in header
    # Check length is ultra compact (< 100 characters, < 35 tokens)
    assert len(header) < 100
