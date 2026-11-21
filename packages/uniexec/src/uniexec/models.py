"""
UniExec Data Models
===================
Pydantic data models for sandbox requests, security results, and execution telemetry.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ASTGuardResult(BaseModel):
    is_safe: bool
    violations: List[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    status: str = "SUCCESS"  # SUCCESS, ERROR, TIMEOUT, BLOCKED
    result: Any = None
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: float = 0.0
    token_savings_percent: float = 98.0
    error: Optional[str] = None

    def to_readable_summary(self) -> str:
        status_sym = "✔ SUCCESS" if self.status == "SUCCESS" else f"❌ {self.status}"
        lines = [
            f"=== UNIBREAK EXECUTION RESULT: {status_sym} ({self.execution_time_ms:.2f}ms) ===",
            f"Status: {self.status}",
            f"Estimated Token Savings: {self.token_savings_percent:.1f}% (vs plain JSON-RPC)"
        ]
        if self.result is not None:
            lines.append(f"\n📦 Return Value:\n{self.result}")
        if self.stdout:
            lines.append(f"\n📄 Stdout:\n{self.stdout}")
        if self.stderr:
            lines.append(f"\n⚠️ Stderr:\n{self.stderr}")
        if self.error:
            lines.append(f"\n🚫 Error:\n{self.error}")
        return "\n".join(lines)
