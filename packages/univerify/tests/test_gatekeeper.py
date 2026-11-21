"""
Unit tests for UniVerify Gatekeeper Facade
"""

import pytest
from univerify.gatekeeper import Gatekeeper


def test_gatekeeper_rejects_code_with_suppress():
    gk = Gatekeeper()
    bad_code = """
    package com.uniai

    @Suppress("UNCHECKED_CAST")
    fun compute(): String = "test"
    """
    res = gk.verify_code(bad_code, filename="Test.kt")
    assert not res.is_passed
    assert res.overall_verdict == "REJECTED"
    assert any("LAW-000-ZERO-SUPPRESS" in b for b in res.blockers)


def test_gatekeeper_ratifies_sound_code():
    gk = Gatekeeper()
    clean_code = """
\"\"\"
Provides secure token parsing.
\"\"\"
def parse_token(token: str) -> str:
    assert token, "Token must be non-empty"
    return token.strip()
"""
    res = gk.verify_code(clean_code, filename="token_parser.py")
    assert res.is_passed
    assert res.overall_verdict == "RATIFIED"
    assert len(res.blockers) == 0


def test_gatekeeper_loop_safety_proven():
    gk = Gatekeeper()
    res = gk.verify_loop_safety(max_iterations=50)
    assert res.is_passed
    assert res.overall_verdict == "RATIFIED"


def test_gatekeeper_bounds_safety_proven():
    gk = Gatekeeper()
    res = gk.verify_bounds_safety(buffer_size=512, min_index=0, max_index=511)
    assert res.is_passed
    assert res.overall_verdict == "RATIFIED"


def test_gatekeeper_bounds_safety_rejected_on_overflow():
    gk = Gatekeeper()
    res = gk.verify_bounds_safety(buffer_size=512, min_index=0, max_index=512)
    assert not res.is_passed
    assert res.overall_verdict == "REJECTED"
    assert len(res.blockers) > 0
