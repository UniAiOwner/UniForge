"""
Kotlin Android & Systems Prime Specialist.
Implements:
  - K2 Compiler FIR Architecture & Delimiter Syntax Balancing (UniWatch integration)
  - Constitutional Law-000: Absolute Zero @Suppress Invariant
  - Law ACC-001: Integer Paise Money Math (Zero-Float in financial models)
  - WCAG & Material 3 Adaptive Minimum Touch Bounds (48dp minimum)
"""

import os
import re
from pathlib import Path
from typing import List, Optional

from .models import (
    TriadLanguage,
    FindingSeverity,
    CodeFinding,
    CodeAuditReport,
)

# UniWatch delimiter parser integration
try:
    from uniwatch.parsers import check_delimiter_balance
    UNIWATCH_AVAILABLE = True
except ImportError:
    UNIWATCH_AVAILABLE = False


class KotlinSpecialist:
    """Specialist engine for Kotlin & Android systems architecture & verification."""

    # Patterns for Constitutional Invariants
    SUPPRESS_PATTERN = re.compile(r'@(?:file:)?Suppress\s*\([^\)]*\)', re.MULTILINE)
    FLOAT_MONEY_PATTERN = re.compile(
        r'(?:val|var)\s+(?:amount|price|balance|total|subtotal|discount|tax|fee|rate)\s*:\s*(?:Float|Double)\b',
        re.IGNORECASE
    )
    TOUCH_TARGET_SUB_48DP = re.compile(r'\.size\s*\(\s*([1-3]?[0-9]|4[0-7])\.dp\s*\)', re.IGNORECASE)
    THREAD_SLEEP_PATTERN = re.compile(r'\bThread\.sleep\s*\(', re.MULTILINE)

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root or os.getcwd()).resolve()

    def audit_code(self, code_text: str, file_path: str = "Component.kt") -> CodeAuditReport:
        """Audits Kotlin source code for delimiter balance, @Suppress, Paise money, and touch targets."""
        findings: List[CodeFinding] = []

        # 1. Delimiter Syntax Check (UniWatch)
        if UNIWATCH_AVAILABLE:
            delim_valid, delim_msg = check_delimiter_balance(code_text, language="kotlin")
            if not delim_valid:
                findings.append(CodeFinding(
                    rule_id="KT-DELIMITER-CORRUPT",
                    severity=FindingSeverity.CRITICAL,
                    file_path=file_path,
                    line_number=1,
                    message=f"Delimiter / Brace Syntax Corruption: {delim_msg}",
                    snippet="Brace/parenthesis mismatch"
                ))

        # 2. Constitutional Law-000: Zero @Suppress Invariant
        for match in self.SUPPRESS_PATTERN.finditer(code_text):
            line_no = code_text[:match.start()].count("\n") + 1
            findings.append(CodeFinding(
                rule_id="LAW-000-ZERO-SUPPRESS",
                severity=FindingSeverity.CRITICAL,
                file_path=file_path,
                line_number=line_no,
                message="Strict Invariant Violation: '@Suppress' is 100% strictly forbidden by Constitutional Law-000.",
                snippet=match.group(0)
            ))

        # 3. Law ACC-001: Integer Paise Money Math (Zero-Float in financial fields)
        is_financial = any(kw in file_path.lower() for kw in ["invoice", "ledger", "bill", "payment", "account", "order", "sale", "pos"])
        for match in self.FLOAT_MONEY_PATTERN.finditer(code_text):
            line_no = code_text[:match.start()].count("\n") + 1
            severity = FindingSeverity.CRITICAL if is_financial else FindingSeverity.WARNING
            findings.append(CodeFinding(
                rule_id="LAW-ACC-001-FLOAT-MONEY",
                severity=severity,
                file_path=file_path,
                line_number=line_no,
                message="Float/Double money detected. Law ACC-001 mandates unboxed integer Long/Int paise to prevent IEEE-754 precision loss.",
                snippet=match.group(0)
            ))

        # 4. Material 3 & WCAG 48dp Minimum Touch Target Bounds
        for match in self.TOUCH_TARGET_SUB_48DP.finditer(code_text):
            line_no = code_text[:match.start()].count("\n") + 1
            findings.append(CodeFinding(
                rule_id="M3-TOUCH-BOUNDS-48DP",
                severity=FindingSeverity.WARNING,
                file_path=file_path,
                line_number=line_no,
                message=f"Touch target {match.group(0)} is below the WCAG / Material 3 48x48dp minimum clickable bounding box.",
                snippet=match.group(0)
            ))

        # 5. Thread.sleep in Kotlin coroutines / UI code
        for match in self.THREAD_SLEEP_PATTERN.finditer(code_text):
            line_no = code_text[:match.start()].count("\n") + 1
            findings.append(CodeFinding(
                rule_id="KT-THREAD-SLEEP-BLOCKING",
                severity=FindingSeverity.CRITICAL,
                file_path=file_path,
                line_number=line_no,
                message="Blocking 'Thread.sleep()' detected. Use 'delay()' from kotlinx.coroutines to avoid stalling the dispatcher.",
                snippet=match.group(0)
            ))

        has_critical = any(f.severity == FindingSeverity.CRITICAL for f in findings)
        return CodeAuditReport(
            language=TriadLanguage.KOTLIN,
            target_path=file_path,
            passed=not has_critical,
            findings=findings,
            summary=f"Kotlin audit: {len(findings)} findings ({sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)} critical)"
        )

    def audit_file(self, full_path: Path) -> CodeAuditReport:
        """Audits a Kotlin source file on disk."""
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
                language=TriadLanguage.KOTLIN,
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
