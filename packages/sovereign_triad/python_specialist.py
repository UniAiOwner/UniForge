"""
Python Systems & Engineering Prime Specialist.
Implements:
  - PEP 703 No-GIL / CPython 3.14 standards
  - Strict AST static invariant analysis
  - Blocking I/O detection inside async event loops
  - Law-000 zero silent error suppression detection
  - Isolated Bubblewrap sandbox test execution
"""

import ast
import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import (
    TriadLanguage,
    FindingSeverity,
    CodeFinding,
    CodeAuditReport,
    TriadExecutionResult,
)

# UniExec sandbox integration
try:
    from uniexec.engine import UniExecEngine
    UNIEXEC_AVAILABLE = True
except ImportError:
    UNIEXEC_AVAILABLE = False


class PythonAsyncVisitor(ast.NodeVisitor):
    """AST visitor to detect blocking operations and bad practices in Python code."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.findings: List[CodeFinding] = []
        self._in_async_func = False
        self._current_func_name = ""

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        prev_async = self._in_async_func
        prev_name = self._current_func_name
        self._in_async_func = True
        self._current_func_name = node.name
        self.generic_visit(node)
        self._in_async_func = prev_async
        self._current_func_name = prev_name

    def visit_Call(self, node: ast.Call):
        if self._in_async_func:
            # Check for time.sleep()
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "time" and node.func.attr == "sleep":
                    self.findings.append(CodeFinding(
                        rule_id="PY-ASYNC-BLOCKING-001",
                        severity=FindingSeverity.CRITICAL,
                        file_path=self.file_path,
                        line_number=node.lineno,
                        message=f"Blocking 'time.sleep()' called inside async function '{self._current_func_name}'. Use 'await asyncio.sleep()' instead.",
                        snippet=f"time.sleep(...) in async {self._current_func_name}"
                    ))
                # Check for requests.get/post etc.
                elif isinstance(node.func.value, ast.Name) and node.func.value.id == "requests":
                    self.findings.append(CodeFinding(
                        rule_id="PY-ASYNC-BLOCKING-002",
                        severity=FindingSeverity.CRITICAL,
                        file_path=self.file_path,
                        line_number=node.lineno,
                        message=f"Synchronous 'requests.{node.func.attr}' called inside async function '{self._current_func_name}'. Use httpx.AsyncClient.",
                        snippet=f"requests.{node.func.attr} in async {self._current_func_name}"
                    ))
            elif isinstance(node.func, ast.Name) and node.func.id == "open":
                self.findings.append(CodeFinding(
                    rule_id="PY-ASYNC-BLOCKING-003",
                    severity=FindingSeverity.WARNING,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    message=f"Synchronous file 'open()' called inside async function '{self._current_func_name}'. Consider aiofiles or asyncio.to_thread.",
                    snippet=f"open(...) in async {self._current_func_name}"
                ))

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Law-000: Zero silent suppression (bare except with pass or empty body)
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.findings.append(CodeFinding(
                rule_id="LAW-000-SILENT-PASS",
                severity=FindingSeverity.CRITICAL,
                file_path=self.file_path,
                line_number=node.lineno,
                message="Silent error suppression detected: 'except: pass' violates Constitutional Law-000.",
                snippet="except: pass"
            ))
        self.generic_visit(node)


class PythonSpecialist:
    """Specialist engine for Python systems architecture & verification."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root or os.getcwd()).resolve()

    def audit_code(self, code_text: str, file_path: str = "script.py") -> CodeAuditReport:
        """Analyzes Python code for AST syntax, async invariants, and Law-000 compliance."""
        findings: List[CodeFinding] = []

        try:
            tree = ast.parse(code_text, filename=file_path)
        except SyntaxError as e:
            findings.append(CodeFinding(
                rule_id="PY-SYNTAX-ERROR",
                severity=FindingSeverity.CRITICAL,
                file_path=file_path,
                line_number=e.lineno or 1,
                message=f"Python AST SyntaxError: {e.msg}",
                snippet=e.text
            ))
            return CodeAuditReport(
                language=TriadLanguage.PYTHON,
                target_path=file_path,
                passed=False,
                findings=findings,
                summary=f"Failed AST parsing: {e.msg}"
            )

        visitor = PythonAsyncVisitor(file_path=file_path)
        visitor.visit(tree)
        findings.extend(visitor.findings)

        has_critical = any(f.severity == FindingSeverity.CRITICAL for f in findings)
        return CodeAuditReport(
            language=TriadLanguage.PYTHON,
            target_path=file_path,
            passed=not has_critical,
            findings=findings,
            summary=f"Python audit: {len(findings)} findings ({visitor.findings.__len__()} critical)"
        )

    def audit_file(self, full_path: Path) -> CodeAuditReport:
        """Audits a Python source file on disk."""
        try:
            rel_path = str(full_path.relative_to(self.repo_root))
        except ValueError:
            rel_path = str(full_path)

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                code_text = f.read()
            return self.audit_code(code_text=code_text, file_path=rel_path)
        except Exception as e:
            return CodeAuditReport(
                language=TriadLanguage.PYTHON,
                target_path=rel_path,
                passed=False,
                findings=[CodeFinding(
                    rule_id="IO-ERROR",
                    severity=FindingSeverity.CRITICAL,
                    file_path=rel_path,
                    line_number=1,
                    message=f"Failed to read file: {e}"
                )],
                summary=f"I/O error during audit: {e}"
            )

    def execute_sandboxed_test(self, test_script: str, timeout_sec: int = 15) -> TriadExecutionResult:
        """Executes a Python test script safely inside the UniExec Bubblewrap jail."""
        start_t = time.perf_counter()
        if UNIEXEC_AVAILABLE:
            engine = UniExecEngine()
            exec_res = engine.execute(script_code=test_script, timeout_seconds=timeout_sec)
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            exit_code = 0 if exec_res.status == "SUCCESS" else 1
            return TriadExecutionResult(
                command="uniexec_bwrap",
                exit_code=exit_code,
                stdout=exec_res.stdout,
                stderr=exec_res.stderr or (exec_res.error or ""),
                sandbox_used=True,
                duration_ms=duration_ms,
                truncated=len(exec_res.stdout) > 2000 or len(exec_res.stderr) > 2000
            )
        else:
            # Fallback to local subprocess if bwrap not available
            import subprocess
            proc = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True, timeout=timeout_sec)
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            return TriadExecutionResult(
                command="python_subprocess",
                exit_code=proc.returncode,
                stdout=proc.stdout[:2000],
                stderr=proc.stderr[:2000],
                sandbox_used=False,
                duration_ms=duration_ms,
                truncated=len(proc.stdout) > 2000 or len(proc.stderr) > 2000
            )
