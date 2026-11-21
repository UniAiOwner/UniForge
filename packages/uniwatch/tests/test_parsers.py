"""
Tests for UniWatch Multi-Language Parsers.
"""

from uniwatch.parsers import (
    validate_python_syntax,
    validate_json_syntax,
    validate_delimiter_balance,
)


def test_python_valid_syntax():
    code = """
def calculate_sum(a: int, b: int) -> int:
    return a + b
"""
    ok, err = validate_python_syntax(code, "valid.py")
    assert ok is True
    assert err is None


def test_python_invalid_syntax():
    code = """
def broken_fn(a, b:
    return a + b
"""
    ok, err = validate_python_syntax(code, "broken.py")
    assert ok is False
    assert "Syntax Error" in err


def test_json_valid_syntax():
    content = '{"name": "UniWatch", "active": true, "count": 42}'
    ok, err = validate_json_syntax(content, "valid.json")
    assert ok is True
    assert err is None


def test_json_invalid_syntax():
    content = '{"name": "UniWatch", "active": true, missing_quote}'
    ok, err = validate_json_syntax(content, "broken.json")
    assert ok is False
    assert "JSON Syntax Error" in err


def test_kotlin_balanced_delimiters():
    code = """
package com.uniai.core

class Engine(val id: String) {
    fun run() {
        val list = listOf(1, 2, 3)
        println("Processing ${list.size} items in engine $id")
    }
}
"""
    ok, err = validate_delimiter_balance(code, "Engine.kt")
    assert ok is True
    assert err is None


def test_kotlin_unbalanced_braces():
    code = """
package com.uniai.core

class Engine {
    fun broken() {
        println("missing closing brace")
}
"""
    ok, err = validate_delimiter_balance(code, "Engine.kt")
    assert ok is False
    assert "Unclosed delimiter '{'" in err


def test_kotlin_mismatched_brackets():
    code = """
val items = listOf(1, 2, 3]
"""
    ok, err = validate_delimiter_balance(code, "Test.kt")
    assert ok is False
    assert "Mismatched ']'" in err


def test_kotlin_char_literals():
    code = """
fun isBracket(c: Char): Boolean {
    return c == '}' || c == ')' || c == ']' || c == '{' || c == '(' || c == '['
}
"""
    ok, err = validate_delimiter_balance(code, "CharTest.kt")
    assert ok is True
    assert err is None
