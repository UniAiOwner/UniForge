"""
Tests for UniWatch Sentinel Bridge (Law-000, Leases, Drift).
"""

from pathlib import Path
from uniwatch.sentinel import (
    check_univerify_invariants,
    check_unibus_lease,
)


def test_invariant_suppress_rejection():
    code = """
@Suppress("UNCHECKED_CAST")
fun castValue(x: Any): String = x as String
"""
    ok, violations = check_univerify_invariants(code, Path("Service.kt"))
    assert ok is False
    assert any("Suppress" in v or "LAW-000" in v for v in violations)


def test_clean_code_invariants():
    code = """
package com.uniai.core
fun cleanValue(x: String): String = x.trim()
"""
    ok, violations = check_univerify_invariants(code, Path("Service.kt"))
    assert ok is True
    assert len(violations) == 0


def test_unibus_lease_check_integration():
    ok, warn = check_unibus_lease(Path("clean_file.py"))
    assert ok is True
