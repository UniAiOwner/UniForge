"""
Domain Models for the Sovereign Coding Triad.
Governs Python Systems, Kotlin Android, and Security AppSec specialist engines.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TriadLanguage(str, Enum):
    PYTHON = "python"
    KOTLIN = "kotlin"
    SECURITY = "security"
    RUST = "rust"
    UNKNOWN = "unknown"


class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class CodeFinding(BaseModel):
    rule_id: str = Field(description="Unique rule or invariant code (e.g. LAW-000, ACC-001, ASYNC-001)")
    severity: FindingSeverity = Field(description="Severity of finding")
    file_path: str = Field(description="Target file relative path")
    line_number: int = Field(default=1, description="Line number where issue was detected")
    message: str = Field(description="Human readable explanation")
    snippet: Optional[str] = Field(default=None, description="Problematic code snippet")


class CodeAuditReport(BaseModel):
    language: TriadLanguage = Field(description="Target language analyzed")
    target_path: str = Field(description="Analyzed path")
    passed: bool = Field(description="Whether the code meets all strict invariants")
    findings: List[CodeFinding] = Field(default_factory=list, description="List of detected findings")
    summary: str = Field(description="Executive summary of audit")

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.WARNING)


class SecretFinding(BaseModel):
    secret_type: str = Field(description="Identified secret pattern or high-entropy token")
    file_path: str = Field(description="File containing the secret")
    line_number: int = Field(description="Line number")
    masked_preview: str = Field(description="Redacted preview of the string")
    shannon_entropy: float = Field(description="Calculated Shannon entropy score")


class SecretScanResult(BaseModel):
    scanned_files_count: int = Field(default=0)
    safe: bool = Field(description="True if zero secrets or leaks detected")
    secrets_found: List[SecretFinding] = Field(default_factory=list)


class Z3SecurityBoundResult(BaseModel):
    invariant_name: str = Field(description="Name of the security invariant")
    satisfiable: bool = Field(description="Whether SMT solver found satisfying solution")
    invariant_proved: bool = Field(description="Whether the safety invariant holds unconditionally")
    counterexample: Optional[str] = Field(default=None, description="Counterexample if invariant fails")
    solve_duration_ms: float = Field(default=0.0)


class TriadExecutionResult(BaseModel):
    command: str = Field(description="Command executed")
    exit_code: int = Field(description="Process return code")
    stdout: str = Field(default="", description="Captured stdout")
    stderr: str = Field(default="", description="Captured stderr")
    sandbox_used: bool = Field(default=False, description="Whether executed inside Bubblewrap jail")
    duration_ms: float = Field(default=0.0, description="Runtime in milliseconds")
    truncated: bool = Field(default=False, description="Whether output was truncated for token efficiency")


class TriadVerificationCertificate(BaseModel):
    target_path: str = Field(description="Path or task target verified")
    overall_passed: bool = Field(description="Overall verification verdict")
    syntax_valid: bool = Field(default=True, description="AST and delimiter syntax validation")
    security_valid: bool = Field(default=True, description="Zero secret leaks and passed security bounds")
    invariants_valid: bool = Field(default=True, description="Constitutional Law-000 zero-shortcut & zero-suppress")
    artifact_soundness_score: float = Field(default=1.0, description="Score based on arXiv:2611.21407")
    details: Dict[str, Any] = Field(default_factory=dict)
