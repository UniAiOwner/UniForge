"""
UniExec - Sovereign Sandboxed Code Mode Runtime
===============================================
Pillar 5 of UniCortex Brain 2.0 Mesh.
Provides Bubblewrap container isolation, AST pre-execution safety inspection,
POSIX resource quotas, and pre-bound local UniCortex primitives.
"""

from uniexec.models import ExecutionResult, ASTGuardResult
from uniexec.ast_guard import ASTSafetyGuard
from uniexec.prelude import UniExecPrelude
from uniexec.sandbox import SandboxOrchestrator
from uniexec.engine import UniExecEngine, get_engine

__all__ = [
    "ExecutionResult",
    "ASTGuardResult",
    "ASTSafetyGuard",
    "UniExecPrelude",
    "SandboxOrchestrator",
    "UniExecEngine",
    "get_engine",
]

__version__ = "2026.1.0"
