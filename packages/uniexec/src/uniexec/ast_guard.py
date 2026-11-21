"""
UniExec Tier 1: Pre-Execution AST Safety Guard
==============================================
Inspects agent scripts at the AST level before spawning the container.
Blocks destructive calls, raw socket network exfiltration, and unsafe execution.
"""

import ast
import re
from typing import List
from uniexec.models import ASTGuardResult

FORBIDDEN_CALLS = {
    "eval": "Unsafe dynamic code evaluation",
    "exec": "Unsafe dynamic code execution",
    "compile": "Unsafe runtime code compilation",
    "__import__": "Direct low-level import",
}

FORBIDDEN_MODULES = {
    "socket": "Network socket creation forbidden in sandbox",
    "urllib": "Direct HTTP request forbidden in sandbox",
    "requests": "Direct HTTP request forbidden in sandbox",
    "httpx": "Direct HTTP request forbidden in sandbox",
    "paramiko": "SSH/remote execution forbidden",
    "ctypes": "Direct memory access / C-FFI forbidden",
}

DESTRUCTIVE_PATTERNS = [
    re.compile(r"\brm\s+-rf\s+[/~]"),
    re.compile(r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),  # fork bomb
    re.compile(r">\s*/dev/sd[a-z]"),
]


class ASTSafetyGuard:

    @staticmethod
    def inspect(script_code: str) -> ASTGuardResult:
        violations: List[str] = []

        if not script_code.strip():
            return ASTGuardResult(is_safe=True, violations=[])

        # 1. Regex check for destructive shell patterns in literals
        for pattern in DESTRUCTIVE_PATTERNS:
            if pattern.search(script_code):
                violations.append("DESTRUCTIVE_PATTERN: Destructive shell pattern detected in script content.")

        # 2. Parse AST
        try:
            tree = ast.parse(script_code)
        except SyntaxError as e:
            return ASTGuardResult(
                is_safe=False,
                violations=[f"SYNTAX_ERROR: Python syntax error at line {e.lineno}: {e.msg}"]
            )

        # 3. Walk AST nodes
        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in FORBIDDEN_CALLS:
                    violations.append(f"FORBIDDEN_CALL: '{func_name}' is disallowed: {FORBIDDEN_CALLS[func_name]}")

            # Check imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod in FORBIDDEN_MODULES:
                        violations.append(f"FORBIDDEN_IMPORT: Module '{root_mod}' is disallowed: {FORBIDDEN_MODULES[root_mod]}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    if root_mod in FORBIDDEN_MODULES:
                        violations.append(f"FORBIDDEN_IMPORT: Module '{root_mod}' is disallowed: {FORBIDDEN_MODULES[root_mod]}")

        is_safe = len(violations) == 0
        return ASTGuardResult(is_safe=is_safe, violations=violations)
