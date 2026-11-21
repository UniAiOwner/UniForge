"""
Unit tests for UniVerify Level 1: Invariant & Security Code Guard
"""

import pytest
from univerify.invariants import InvariantGuard


def test_suppress_annotation_violation():
    guard = InvariantGuard()
    bad_code = """
    package com.uniai.core

    @Suppress("UNCHECKED_CAST")
    fun unsafeCast(obj: Any): String {
        return obj as String
    }
    """
    res = guard.check_code(bad_code, filename="Service.kt")
    assert not res.passed
    assert any(v.rule_name == "LAW-000-ZERO-SUPPRESS" for v in res.violations)


def test_fake_pass_shortcut_violation():
    guard = InvariantGuard()
    bad_code = """
    def verify_auth_token(token: str) -> bool:
        # Skip actual check for now
        return true // TODO fake pass
    """
    res = guard.check_code(bad_code, filename="auth.py")
    assert not res.passed
    assert any("LAW-000-SHORTCUT" in v.rule_name for v in res.violations)


def test_todo_stub_throw_violation():
    guard = InvariantGuard()
    bad_code = """
    fun renderUi() {
        TODO("not implemented")
    }
    """
    res = guard.check_code(bad_code, filename="Screen.kt")
    assert not res.passed
    assert any("LAW-000-SHORTCUT" in v.rule_name for v in res.violations)


def test_secret_leak_violation():
    guard = InvariantGuard()
    # Construct synthetic Google API key (AIza followed by 35 characters)
    part1 = "AIza" + "Sy"
    fake_key = f'API_KEY = "{part1}' + ('A' * 33) + '"'
    bad_code = f"""
    import os
    {fake_key}
    """
    res = guard.check_code(bad_code, filename="config.py")
    assert not res.passed
    assert any(v.rule_name == "SECRET-LEAK-DETECTED" for v in res.violations)


def test_unsafe_dynamic_exec_violation():
    guard = InvariantGuard()
    bad_code = """
    def execute_payload(raw_code: str):
        eval(raw_code)
    """
    res = guard.check_code(bad_code, filename="executor.py")
    assert not res.passed
    assert any(v.rule_name == "UNSAFE-DYNAMIC-EXEC" for v in res.violations)


def test_clean_code_passes():
    guard = InvariantGuard()
    clean_code = """
    \"\"\"Calculates token savings ratio.\"\"\"
    def calculate_token_savings(original_tokens: int, economized_tokens: int) -> float:
        assert original_tokens > 0, "Original tokens must be positive"
        assert economized_tokens >= 0, "Economized tokens cannot be negative"
        savings = (original_tokens - economized_tokens) / original_tokens
        return round(savings, 4)
    """
    res = guard.check_code(clean_code, filename="savings.py")
    assert res.passed
    assert len(res.violations) == 0
