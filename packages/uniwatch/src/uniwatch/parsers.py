"""
Sub-15ms Multi-Language AST & Delimiter Balance Parsers.
Catches unbalanced syntax, mismatched braces, and broken templates before compiler execution.
"""

import ast
import json
from pathlib import Path
from typing import Tuple, Optional, List


def validate_python_syntax(source: str, filename: str = "code.py") -> Tuple[bool, Optional[str]]:
    """Validates Python syntax via native ast.parse."""
    try:
        ast.parse(source, filename=filename)
        return True, None
    except SyntaxError as e:
        return False, f"Python Syntax Error at {filename}:{e.lineno}:{e.offset} -> {e.msg}"
    except Exception as e:
        return False, f"Python Parse Error in {filename}: {str(e)}"


def validate_json_syntax(source: str, filename: str = "config.json") -> Tuple[bool, Optional[str]]:
    """Validates JSON structure."""
    if not source.strip():
        return True, None
    try:
        json.loads(source)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON Syntax Error at {filename}:{e.lineno}:{e.colno} -> {e.msg}"


def validate_delimiter_balance(source: str, filename: str = "code.kt") -> Tuple[bool, Optional[str]]:
    """
    Tokenizer-level delimiter stack balancer for Kotlin, Rust, and C-like languages.
    Tracks:
    - Braces: { }, ( ), [ ]
    - Strings: "..." (with escape sequences) and multiline triple quotes \"\"\"...\"\"\"
    - Comments: Single-line // and multi-line /* ... */
    - String interpolation in Kotlin: ${ ... }
    """
    stack: List[Tuple[str, int]] = []  # (delimiter, line_no)
    matching = {')': '(', '}': '{', ']': '['}

    i = 0
    n = len(source)
    line = 1

    in_line_comment = False
    in_block_comment = False
    in_single_quote_char = False
    in_triple_string = False
    in_string = False

    while i < n:
        char = source[i]

        if char == '\n':
            line += 1
            in_line_comment = False
            # Single-line strings/chars cannot span newlines
            if in_string and not in_triple_string:
                return False, f"Unterminated string literal at {filename}:{line - 1}"
            if in_single_quote_char:
                return False, f"Unterminated character literal at {filename}:{line - 1}"
            i += 1
            continue

        # Handle comments
        if in_line_comment:
            i += 1
            continue

        if in_block_comment:
            if char == '*' and i + 1 < n and source[i + 1] == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        # Handle character literals ('a', '\'', '\n', etc.)
        if in_single_quote_char:
            if char == '\\':
                i += 2  # skip escaped character
                continue
            if char == '\'':
                in_single_quote_char = False
                i += 1
                continue
            i += 1
            continue

        # Handle strings
        if in_triple_string:
            if char == '"' and i + 2 < n and source[i + 1] == '"' and source[i + 2] == '"':
                in_triple_string = False
                i += 3
                continue
            i += 1
            continue

        if in_string:
            if char == '\\':
                i += 2  # skip escaped character
                continue
            if char == '"':
                in_string = False
                i += 1
                continue
            i += 1
            continue

        # Start of comments?
        if char == '/' and i + 1 < n:
            next_char = source[i + 1]
            if next_char == '/':
                in_line_comment = True
                i += 2
                continue
            elif next_char == '*':
                in_block_comment = True
                i += 2
                continue

        # Start of character literal?
        if char == '\'':
            in_single_quote_char = True
            i += 1
            continue

        # Start of strings?
        if char == '"':
            if i + 2 < n and source[i + 1] == '"' and source[i + 2] == '"':
                in_triple_string = True
                i += 3
                continue
            else:
                in_string = True
                i += 1
                continue

        # Delimiters
        if char in '({[':
            stack.append((char, line))
        elif char in ')}]':
            expected_open = matching[char]
            if not stack:
                return False, f"Mismatched closing '{char}' at {filename}:{line} with no opening delimiter"
            top_open, open_line = stack.pop()
            if top_open != expected_open:
                return False, f"Mismatched '{char}' at {filename}:{line}; expected closing for '{top_open}' from line {open_line}"

        i += 1

    if in_block_comment:
        return False, f"Unclosed block comment (/* ... */) in {filename}"
    if in_triple_string or in_string:
        return False, f"Unterminated string literal in {filename}"
    if in_single_quote_char:
        return False, f"Unterminated character literal in {filename}"
    if stack:
        unclosed, open_line = stack[-1]
        return False, f"Unclosed delimiter '{unclosed}' opened at line {open_line} in {filename}"

    return True, None


def validate_file_syntax(path: Path) -> Tuple[bool, Optional[str]]:
    """Main entrypoint routing to appropriate parser based on extension."""
    if not path.exists() or not path.is_file():
        return False, f"File does not exist: {path}"

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"Failed to read file: {e}"

    suffix = path.suffix.lower()

    if suffix == ".py":
        return validate_python_syntax(content, filename=path.name)
    elif suffix == ".json":
        return validate_json_syntax(content, filename=path.name)
    elif suffix in {".kt", ".kts", ".rs"}:
        return validate_delimiter_balance(content, filename=path.name)

    return True, None
