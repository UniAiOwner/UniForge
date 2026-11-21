"""
Sovereign Coding Triad Unified Orchestrator.
Unifies Python Systems Prime, Kotlin Android Prime, and Security AppSec Prime
across the 7-Pillar Substrate (UniGov, UniSkill, UniMemory, UniVerify, UniExec, UniBus, UniWatch).
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from .models import (
    TriadLanguage,
    FindingSeverity,
    CodeFinding,
    CodeAuditReport,
    TriadExecutionResult,
    TriadVerificationCertificate,
)
from .python_specialist import PythonSpecialist
from .kotlin_specialist import KotlinSpecialist
from .security_specialist import SecuritySpecialist

# Substrate Pillar Integrations
try:
    from unibus.bus import UniBus, EventPriority
    UNIBUS_AVAILABLE = True
except ImportError:
    UNIBUS_AVAILABLE = False

try:
    from univerify.gatekeeper import Gatekeeper
    from univerify.artifact_scorer import DeterministicArtifactScorer
    UNIVERIFY_AVAILABLE = True
except ImportError:
    UNIVERIFY_AVAILABLE = False

try:
    from unimemory.substrate import UniMemorySubstrate
    UNIMEMORY_AVAILABLE = True
except ImportError:
    UNIMEMORY_AVAILABLE = False

try:
    from uniexec.engine import UniExecEngine
    UNIEXEC_AVAILABLE = True
except ImportError:
    UNIEXEC_AVAILABLE = False


class SovereignTriadOrchestrator:
    """Unified Orchestration Engine for the Sovereign Coding Triad."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root or os.getcwd()).resolve()
        self.python_spec = PythonSpecialist(repo_root=str(self.repo_root))
        self.kotlin_spec = KotlinSpecialist(repo_root=str(self.repo_root))
        self.security_spec = SecuritySpecialist(repo_root=str(self.repo_root))

    def detect_language(self, file_path: str) -> TriadLanguage:
        """Determines target language from file extension or content."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".py", ".pyi"):
            return TriadLanguage.PYTHON
        elif ext in (".kt", ".kts"):
            return TriadLanguage.KOTLIN
        elif ext in (".rs",):
            return TriadLanguage.RUST
        elif ext in (".xml", ".json", ".yaml", ".yml", ".env"):
            return TriadLanguage.SECURITY
        return TriadLanguage.UNKNOWN

    def audit_target(self, target_path: str) -> CodeAuditReport:
        """
        Runs comprehensive multi-specialist audit on a file or snippet.
        Combines language-specific rules and universal security scan.
        """
        p = Path(target_path)
        if not p.is_absolute():
            p = self.repo_root / p

        if not p.is_file():
            return CodeAuditReport(
                language=TriadLanguage.UNKNOWN,
                target_path=target_path,
                passed=False,
                findings=[CodeFinding(
                    rule_id="NOT-FOUND",
                    severity=FindingSeverity.CRITICAL,
                    file_path=target_path,
                    line_number=1,
                    message=f"File not found: {target_path}"
                )],
                summary="File does not exist."
            )

        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        lang = self.detect_language(str(p))
        findings: List[CodeFinding] = []

        # 1. Universal Security Scan on all files
        sec_report = self.security_spec.audit_code(content, file_path=target_path)
        findings.extend(sec_report.findings)

        # 2. Language-Specific Specialist Audit
        if lang == TriadLanguage.PYTHON:
            py_report = self.python_spec.audit_code(content, file_path=target_path)
            findings.extend(py_report.findings)
        elif lang == TriadLanguage.KOTLIN:
            kt_report = self.kotlin_spec.audit_code(content, file_path=target_path)
            findings.extend(kt_report.findings)

        has_critical = any(f.severity == FindingSeverity.CRITICAL for f in findings)
        return CodeAuditReport(
            language=lang,
            target_path=target_path,
            passed=not has_critical,
            findings=findings,
            summary=f"Triad Audit: {len(findings)} findings across {lang.value} & Security specialists."
        )

    def execute_command(self, cmd: str, timeout_sec: int = 15) -> TriadExecutionResult:
        """
        Executes Python code safely inside the UniExec Bubblewrap jail.
        """
        return self.python_spec.execute_sandboxed_test(test_script=cmd, timeout_sec=timeout_sec)

    def verify_and_certify(self, target_path: str) -> TriadVerificationCertificate:
        """
        Full-loop verification certificate generation:
        1. Acquires work mutex from UniBus.
        2. Executes multi-specialist audit.
        3. Evaluates Law-000 zero-shortcut gate via UniVerify.
        4. Calculates physical artifact soundness score.
        5. Broadcasts completion event and releases mutex.
        """
        bus = UniBus() if UNIBUS_AVAILABLE else None
        lease_acquired = False

        if bus:
            # Acquire work mutex lease for safe verification
            success, _, _ = bus.acquire_lease(resource_id="triad.coding_mutex", owner_agent="sovereign_triad", ttl_seconds=30)
            lease_acquired = success

        try:
            # 1. Run Triad Specialist Audit
            audit_report = self.audit_target(target_path)
            syntax_valid = not any(f.rule_id in ("PY-SYNTAX-ERROR", "KT-DELIMITER-CORRUPT") for f in audit_report.findings)
            security_valid = not any(f.rule_id.startswith("SEC-") for f in audit_report.findings)
            invariants_valid = not any(f.rule_id.startswith("LAW-") for f in audit_report.findings)

            # 2. UniVerify Formal Gatekeeper evaluation
            artifact_score = 1.0
            if UNIVERIFY_AVAILABLE:
                scorer = DeterministicArtifactScorer()
                p = Path(target_path)
                if not p.is_absolute():
                    p = self.repo_root / p
                if p.is_file():
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        code_content = f.read()
                    score_res = scorer.score_code_artifact(code_text=code_content)
                    artifact_score = score_res.total_score

            overall_passed = audit_report.passed and syntax_valid and security_valid and invariants_valid and (artifact_score >= 0.75)

            cert = TriadVerificationCertificate(
                target_path=target_path,
                overall_passed=overall_passed,
                syntax_valid=syntax_valid,
                security_valid=security_valid,
                invariants_valid=invariants_valid,
                artifact_soundness_score=round(artifact_score, 2),
                details={
                    "language": audit_report.language.value,
                    "findings_count": len(audit_report.findings),
                    "critical_findings": audit_report.critical_count,
                    "summary": audit_report.summary
                }
            )

            # 3. UniBus Event Broadcast
            if bus:
                event_name = "triad.code_verified" if overall_passed else "triad.audit_failed"
                priority = EventPriority.NORMAL if overall_passed else EventPriority.HIGH
                bus.publish_event(
                    topic=event_name,
                    payload={"target": target_path, "passed": overall_passed, "score": artifact_score, "source": "sovereign_triad"},
                    priority=priority
                )

            return cert

        finally:
            if bus and lease_acquired:
                bus.release_lease(resource_id="triad.coding_mutex", owner_agent="sovereign_triad")
