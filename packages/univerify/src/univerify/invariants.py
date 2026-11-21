"""
UniVerify Level 1: Constitutional Invariant & Security Code Guard
=================================================================
Enforces Constitutional Law-000 (Zero Shortcuts, Zero @Suppress, Zero Stubs),
Constitutional Law ACC-001 (Zero Floating-Point Currency),
Zero-Secret Leakage defense, and Safe Execution boundaries.
"""

import re
from typing import Dict, Any, List, Optional
from univerify.models import InvariantCheckResult, InvariantViolation

SECRET_REGEXES = {
    "Google API Key": re.compile(r"AI" + r"za[0-9A-Za-z\-_]{35}"),
    "GitHub Token": re.compile(r"(?:gh" + r"p_[0-9A-Za-z]{36}|github_pat_[0-9A-Za-z_]{40,})"),
    "OpenAI Secret Key": re.compile(r"sk" + r"-[a-zA-Z0-9_-]{32,}"),
    "AWS Access Key": re.compile(r"AK" + r"IA[0-9A-Z]{16}"),
    "Private Key Block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

UNSAFE_PATTERNS = {
    "Unsafe Dynamic Python Eval": re.compile(r"\b(?:eval|exec)\s*\("),
    "Destructive Shell Command": re.compile(r"\brm\s+-rf\s+[/~]"),
    "Unwhitelisted Shell Subprocess": re.compile(r"shell\s*=\s*True"),
}

FAKE_PASS_PATTERNS = {
    "Fake Mock Pass Return": re.compile(r"return\s+(?:true|True)\s*//\s*(?:TODO|mock|fake|pass)", re.IGNORECASE),
    "Unimplemented TODO Throw": re.compile(r'TODO\s*\(\s*["\'](?:not implemented|implement later|stub)["\']\s*\)', re.IGNORECASE),
}

CURRENCY_KEYWORDS = {"price", "amount", "balance", "tax", "discount", "paise", "total", "fee", "subtotal"}


class InvariantGuard:

    @classmethod
    def check_code(cls, code_or_patch: str, filename: str = "code") -> InvariantCheckResult:
        """Runs Level 1 checks across the input code or patch string."""
        violations: List[InvariantViolation] = []
        lines = code_or_patch.splitlines()

        for idx, line in enumerate(lines):
            line_no = idx + 1
            trimmed = line.strip()
            if not trimmed:
                continue

            # 1. Zero @Suppress Rule (Constitutional Law-000)
            if re.search(r"^\s*@(?:Suppress|suppress)\b", trimmed):
                violations.append(InvariantViolation(
                    rule_name="LAW-000-ZERO-SUPPRESS",
                    severity="CRITICAL",
                    line_number=line_no,
                    snippet=trimmed[:120],
                    explanation="Forbidden @Suppress annotation detected. All compiler/linter warnings must be solved via structural refactoring."
                ))

            # 2. Fake Pass / Shortcut Detector (Constitutional Law-000)
            for fake_name, regex in FAKE_PASS_PATTERNS.items():
                if regex.search(trimmed):
                    violations.append(InvariantViolation(
                        rule_name=f"LAW-000-SHORTCUT: {fake_name}",
                        severity="CRITICAL",
                        line_number=line_no,
                        snippet=trimmed[:120],
                        explanation="Fake pass or mock shortcut detected. Real domain implementation required."
                    ))

            # 3. Secret Signatures Scrubber
            for secret_name, regex in SECRET_REGEXES.items():
                if regex.search(trimmed):
                    violations.append(InvariantViolation(
                        rule_name="SECRET-LEAK-DETECTED",
                        severity="CRITICAL",
                        line_number=line_no,
                        snippet="[REDACTED SECRET SIGNATURE]",
                        explanation=f"Potential hardcoded {secret_name} detected in diff/source."
                    ))

            # 4. Unsafe Code Execution
            for unsafe_name, regex in UNSAFE_PATTERNS.items():
                if regex.search(trimmed):
                    violations.append(InvariantViolation(
                        rule_name="UNSAFE-DYNAMIC-EXEC",
                        severity="CRITICAL",
                        line_number=line_no,
                        snippet=trimmed[:120],
                        explanation=f"Dangerous dynamic execution or destructive call: {unsafe_name}."
                    ))

            # 5. Law ACC-001 Integer Paise (Floating-Point Currency Detection)
            trimmed_lower = trimmed.lower()
            if any(k in trimmed_lower for k in CURRENCY_KEYWORDS):
                if re.search(r":\s*(?:Double|Float)\b", trimmed) or re.search(r"\b(?:double|float)\s+[a-zA-Z0-9_]*[Pp]rice", trimmed):
                    violations.append(InvariantViolation(
                        rule_name="LAW-ACC-001-INTEGER-PAISE",
                        severity="CRITICAL",
                        line_number=line_no,
                        snippet=trimmed[:120],
                        explanation="Floating-point Double/Float currency type detected. Law ACC-001 strictly mandates Integer Paise (Long/Int) to prevent rounding drift."
                    ))

        has_critical = any(v.severity == "CRITICAL" for v in violations)
        return InvariantCheckResult(
            passed=(not has_critical),
            violations=violations
        )
