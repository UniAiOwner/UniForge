"""
UniVerify Data Models
=====================
Strict Pydantic models for all 4 verification levels.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class InvariantViolation(BaseModel):
    rule_name: str
    severity: str  # CRITICAL, HIGH, WARNING
    line_number: Optional[int] = None
    snippet: str = ""
    explanation: str = ""


class InvariantCheckResult(BaseModel):
    passed: bool
    violations: List[InvariantViolation] = Field(default_factory=list)


class Z3ProofResult(BaseModel):
    invariant_name: str
    is_satisfied: bool
    proof_status: str  # PROVEN, VIOLATION_DETECTED, UNSAT
    counter_example: Optional[Dict[str, Any]] = None
    mathematical_rationale: str = ""


class ArtifactScoreResult(BaseModel):
    total_score: float = 0.0  # 0.0 to 1.0
    is_sound: bool = False   # True if score >= 0.75 and zero critical flaws
    syntax_score: float = 0.0
    invariant_score: float = 0.0
    evidence_score: float = 0.0
    literature_score: float = 0.0
    failure_reasons: List[str] = Field(default_factory=list)


class TestRunResult(BaseModel):
    command: str = ""
    exit_code: int = 0
    passed: bool = True
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    duration_sec: float = 0.0
    output_summary: str = ""
    failures: List[str] = Field(default_factory=list)


class GateResult(BaseModel):
    is_passed: bool
    level1_invariants: InvariantCheckResult
    level2_z3_proofs: List[Z3ProofResult] = Field(default_factory=list)
    level3_artifact_score: ArtifactScoreResult
    level4_test_run: Optional[TestRunResult] = None
    overall_verdict: str  # RATIFIED, REJECTED, CONDITIONAL
    latency_ms: float = 0.0
    blockers: List[str] = Field(default_factory=list)

    def to_readable_summary(self) -> str:
        status_sym = "✔ RATIFIED (100% SOUND)" if self.is_passed else "❌ REJECTED (FAIL-CLOSED GATE)"
        lines = [
            f"=== UNIVERIFY GATE RESULT: {status_sym} (Latency: {self.latency_ms:.2f}ms) ===",
            f"Overall Verdict: {self.overall_verdict}"
        ]

        if not self.is_passed and self.blockers:
            lines.append("\n🚫 [GATE BLOCKERS]")
            for b in self.blockers:
                lines.append(f"  • {b}")

        lines.append(f"\nLevel 1: Invariant Guard: {'PASSED' if self.level1_invariants.passed else 'FAILED'}")
        for v in self.level1_invariants.violations:
            loc = f":{v.line_number}" if v.line_number else ""
            lines.append(f"  • [{v.severity}] {v.rule_name}{loc}: {v.explanation}")

        if self.level2_z3_proofs:
            lines.append("\nLevel 2: Formal Z3 SMT Proofs:")
            for p in self.level2_z3_proofs:
                p_sym = "PROVEN" if p.is_satisfied else "FAILED"
                lines.append(f"  • [{p_sym}] {p.invariant_name}: {p.mathematical_rationale}")
                if p.counter_example:
                    lines.append(f"    Counter-Example: {p.counter_example}")

        lines.append(f"\nLevel 3: Artifact Score: {self.level3_artifact_score.total_score:.2f} (Sound: {self.level3_artifact_score.is_sound})")
        if self.level3_artifact_score.failure_reasons:
            for fr in self.level3_artifact_score.failure_reasons:
                lines.append(f"  • {fr}")

        if self.level4_test_run:
            t_status = "PASSED" if self.level4_test_run.passed else "FAILED"
            lines.append(f"\nLevel 4: Test Harness: {t_status} (Command: {self.level4_test_run.command})")
            lines.append(f"  • Total: {self.level4_test_run.total_tests}, Passed: {self.level4_test_run.passed_tests}, Failed: {self.level4_test_run.failed_tests} in {self.level4_test_run.duration_sec:.2f}s")
            for f in self.level4_test_run.failures[:5]:
                lines.append(f"    - {f}")

        return "\n".join(lines)
