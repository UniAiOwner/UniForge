"""
UniVerify Level 3: Deterministic Physical Artifact Scorer
=========================================================
Prevents 'ghost exit' failures by requiring concrete, verifiable evidence
and deterministic scoring bounds (score >= 0.75 for sound artifacts).
Based on arXiv:2611.21407 ('Harness Leverage Across Model Size').
"""

import ast
import re
from typing import Dict, Any, List, Optional
from univerify.models import ArtifactScoreResult


class DeterministicArtifactScorer:
    """
    Evaluates source code and architectural artifacts against strict physical invariants.
    """

    @staticmethod
    def score_code_artifact(code_text: str, filename: str = "code.py") -> ArtifactScoreResult:
        """
        Scores a code artifact on AST syntax, typed contracts, testability/evidence,
        and zero-shortcut discipline.
        """
        failure_reasons: List[str] = []
        syntax_score = 0.0
        invariant_score = 0.0
        evidence_score = 0.0
        discipline_score = 0.0

        if not code_text.strip():
            return ArtifactScoreResult(
                total_score=0.0,
                is_sound=False,
                failure_reasons=["Empty artifact content."]
            )

        # 1. Syntax & AST Parseability (0.30 max)
        is_python = filename.endswith(".py")
        if is_python:
            try:
                tree = ast.parse(code_text)
                syntax_score = 0.30
            except SyntaxError as e:
                syntax_score = 0.0
                failure_reasons.append(f"Python Syntax Error at line {e.lineno}: {e.msg}")
        else:
            # Bracket balance check for non-python (Kotlin, Rust, TS, etc.)
            stack = []
            matching = {')': '(', '}': '{', ']': '['}
            balanced = True
            for char in code_text:
                if char in '({[':
                    stack.append(char)
                elif char in ')}]':
                    if not stack or stack[-1] != matching[char]:
                        balanced = False
                        break
                    stack.pop()
            if balanced and not stack:
                syntax_score = 0.30
            else:
                syntax_score = 0.05
                failure_reasons.append("Unbalanced brackets/braces in source code.")

        # 2. Structural Discipline & Typing (0.25 max)
        # Check for type annotations or typed signatures, docstrings, function definitions
        has_functions = bool(re.search(r'\b(def|fun|fn|function|class)\b', code_text))
        has_typing = bool(re.search(r'(:\s*[A-Z][a-zA-Z0-9_\[\]]+|->\s*[A-Z][a-zA-Z0-9_\[\]]+|val\s+\w+:\s*|let\s+\w+:\s*)', code_text))
        has_docs = bool(re.search(r'("""|\'\'\'|/\*\*|///)', code_text))

        if has_functions and has_typing and has_docs:
            invariant_score = 0.25
        elif has_functions and (has_typing or has_docs):
            invariant_score = 0.18
        elif has_functions:
            invariant_score = 0.10
        else:
            invariant_score = 0.05
            failure_reasons.append("Lack of structured function definitions and typed contracts.")

        # 3. Testability & Empirical Evidence (0.25 max)
        # Check for asserts, test cases, return statements, error handling
        has_asserts_or_returns = bool(re.search(r'\b(return|assert|require|check|throw|raise)\b', code_text))
        has_error_handling = bool(re.search(r'\b(try|except|catch|Result|Option|match)\b', code_text))

        if has_asserts_or_returns and has_error_handling:
            evidence_score = 0.25
        elif has_asserts_or_returns:
            evidence_score = 0.15
        else:
            evidence_score = 0.05
            failure_reasons.append("Missing explicit error handling and assertion gates.")

        # 4. Zero-Shortcut Discipline (0.20 max)
        # Check against fake passes, TODO stubs, mock returns
        has_todo_stub = bool(re.search(r'\b(TODO|FIXME|XXX|mockPass|return true // TODO)\b', code_text, re.IGNORECASE))
        has_pass_only = bool(re.search(r'def\s+\w+\([^)]*\):\s*\n\s*pass\b', code_text))

        if not has_todo_stub and not has_pass_only:
            discipline_score = 0.20
        elif has_todo_stub and not has_pass_only:
            discipline_score = 0.10
            failure_reasons.append("Found pending TODO/FIXME placeholder in code.")
        else:
            discipline_score = 0.0
            failure_reasons.append("Found empty 'pass' stub pretending to implement logic.")

        total_score = round(syntax_score + invariant_score + evidence_score + discipline_score, 3)
        is_sound = (total_score >= 0.75) and (syntax_score >= 0.25) and not any("Syntax Error" in r or "Unbalanced" in r for r in failure_reasons)

        return ArtifactScoreResult(
            total_score=total_score,
            is_sound=is_sound,
            syntax_score=round(syntax_score, 3),
            invariant_score=round(invariant_score, 3),
            evidence_score=round(evidence_score, 3),
            literature_score=round(discipline_score, 3),
            failure_reasons=failure_reasons
        )

    @staticmethod
    def score_proposal_artifact(data: Dict[str, Any]) -> ArtifactScoreResult:
        """
        Evaluates scientific, architectural proposals against the 4-pillar benchmark:
        1. Literature Grounding (0.35 max)
        2. Architectural Patterns (0.20 max)
        3. Implementation Steps (0.25 max)
        4. Invariant Constraints (0.20 max)
        """
        citations = data.get("citations", [])
        patterns = data.get("patterns", [])
        steps = data.get("steps", [])
        invariants = data.get("invariants", [])

        score = 0.0
        failure_reasons = []

        # Pillar 1: Literature Grounding (0.35)
        if len(citations) >= 3:
            lit_score = 0.35
        elif len(citations) >= 1:
            lit_score = 0.20
        else:
            lit_score = 0.0
            failure_reasons.append("Zero research literature citations (requires arXiv/empirical grounding).")

        # Pillar 2: Architectural Patterns (0.20)
        if len(patterns) >= 2:
            pat_score = 0.20
        elif len(patterns) >= 1:
            pat_score = 0.10
        else:
            pat_score = 0.0
            failure_reasons.append("No explicit architectural design patterns identified.")

        # Pillar 3: Actionable Steps (0.25)
        if len(steps) >= 3:
            step_score = 0.25
        elif len(steps) >= 1:
            step_score = 0.15
        else:
            step_score = 0.0
            failure_reasons.append("Fewer than 3 actionable implementation steps.")

        # Pillar 4: Hard Invariants (0.20)
        if len(invariants) >= 2:
            inv_score = 0.20
        elif len(invariants) >= 1:
            inv_score = 0.10
        else:
            inv_score = 0.0
            failure_reasons.append("Zero verifiable formal invariants declared.")

        total_score = round(lit_score + pat_score + step_score + inv_score, 3)
        is_sound = (total_score >= 0.75) and (len(citations) > 0) and (len(invariants) > 0)

        return ArtifactScoreResult(
            total_score=total_score,
            is_sound=is_sound,
            syntax_score=step_score,
            invariant_score=inv_score,
            evidence_score=pat_score,
            literature_score=lit_score,
            failure_reasons=failure_reasons
        )
