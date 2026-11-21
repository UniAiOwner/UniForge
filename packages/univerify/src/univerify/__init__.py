"""
UniVerify - Sovereign Invariant & Formal Verification Engine
=============================================================
Pillar 4 of UniCortex Brain 2.0 Mesh.
Provides Level 1 Invariant Rules, Level 2 Z3 SMT Formal Proofs,
Level 3 Deterministic Physical Artifact Scoring (arXiv:2611.21407),
and Level 4 Empirical Test Harness Execution.
"""

from univerify.models import (
    InvariantViolation,
    InvariantCheckResult,
    Z3ProofResult,
    ArtifactScoreResult,
    TestRunResult,
    GateResult,
)
from univerify.invariants import InvariantGuard
from univerify.z3_prover import FormalZ3Prover
from univerify.artifact_scorer import DeterministicArtifactScorer
from univerify.test_runner import TestRunner
from univerify.gatekeeper import Gatekeeper

__all__ = [
    "InvariantViolation",
    "InvariantCheckResult",
    "Z3ProofResult",
    "ArtifactScoreResult",
    "TestRunResult",
    "GateResult",
    "InvariantGuard",
    "FormalZ3Prover",
    "DeterministicArtifactScorer",
    "TestRunner",
    "Gatekeeper",
]

__version__ = "0.1.0"
