"""
Unit tests for UniVerify Level 3: Deterministic Physical Artifact Scorer (arXiv:2611.21407)
"""

import pytest
from univerify.artifact_scorer import DeterministicArtifactScorer


def test_empty_artifact_score():
    scorer = DeterministicArtifactScorer()
    res = scorer.score_code_artifact("", filename="empty.py")
    assert not res.is_sound
    assert res.total_score == 0.0
    assert "Empty artifact content." in res.failure_reasons


def test_python_syntax_error_fails():
    scorer = DeterministicArtifactScorer()
    bad_syntax = "def broken_func(\n    print('unclosed'"
    res = scorer.score_code_artifact(bad_syntax, filename="bad.py")
    assert not res.is_sound
    assert any("Python Syntax Error" in r for r in res.failure_reasons)


def test_unbalanced_brackets_fails_non_python():
    scorer = DeterministicArtifactScorer()
    bad_kotlin = "fun broken() { if (true) { return 1; }"  # missing closing brace
    res = scorer.score_code_artifact(bad_kotlin, filename="broken.kt")
    assert not res.is_sound
    assert any("Unbalanced brackets" in r for r in res.failure_reasons)


def test_well_structured_code_passes_soundness():
    scorer = DeterministicArtifactScorer()
    sound_code = """
\"\"\"
Calculates factorial deterministically.
\"\"\"
def factorial(n: int) -> int:
    assert n >= 0, "n must be non-negative"
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
"""
    res = scorer.score_code_artifact(sound_code, filename="math_utils.py")
    assert res.is_sound
    assert res.total_score >= 0.75
    assert len(res.failure_reasons) == 0


def test_proposal_artifact_soundness():
    scorer = DeterministicArtifactScorer()
    valid_proposal = {
        "citations": [
            {"arxiv_id": "arXiv:2611.21407", "title": "Harness Leverage"},
            {"arxiv_id": "arXiv:2611.19123", "title": "Beyond Plain MCP"},
            {"arxiv_id": "arXiv:2611.18533", "title": "ModHarness-RL"}
        ],
        "patterns": ["Code Mode Sandboxing", "AST Return Filtering"],
        "steps": [
            "Step 1: Ground domain contracts.",
            "Step 2: Implement bubblewrap executor.",
            "Step 3: Connect FastMCP tools."
        ],
        "invariants": ["Zero shortcuts Law-000", "Z3 SMT bounds proof"]
    }
    res = scorer.score_proposal_artifact(valid_proposal)
    assert res.is_sound
    assert res.total_score >= 0.75
    assert len(res.failure_reasons) == 0
