"""
Unit tests for UniExec Tier 1: AST Safety Guard
"""

import pytest
from uniexec.ast_guard import ASTSafetyGuard


def test_clean_script_passes():
    script = """
x = 10
y = 20
result = x + y
"""
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is True
    assert len(res.violations) == 0


def test_eval_blocked():
    script = "eval('1 + 1')"
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is False
    assert any("FORBIDDEN_CALL: 'eval'" in v for v in res.violations)


def test_exec_blocked():
    script = "exec('import os')"
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is False
    assert any("FORBIDDEN_CALL: 'exec'" in v for v in res.violations)


def test_socket_import_blocked():
    script = "import socket\ns = socket.socket()"
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is False
    assert any("FORBIDDEN_IMPORT: Module 'socket'" in v for v in res.violations)


def test_requests_import_blocked():
    script = "from requests import get"
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is False
    assert any("FORBIDDEN_IMPORT: Module 'requests'" in v for v in res.violations)


def test_destructive_shell_pattern_blocked():
    script = 'cmd = "rm -rf /"'
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is False
    assert any("DESTRUCTIVE_PATTERN" in v for v in res.violations)


def test_syntax_error_blocked():
    script = "def broken(:\n    pass"
    res = ASTSafetyGuard.inspect(script)
    assert res.is_safe is False
    assert any("SYNTAX_ERROR" in v for v in res.violations)
