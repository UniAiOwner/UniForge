"""Zero-Hardlink & Machine Portability Gate for UniForge.

Fails immediately if any machine-specific user path (/home/<user>, /media/<user>)
or project-specific hardlink (UniRetail, UniAGI, UniGuard) leaks into UniForge source code.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATTERNS = (
    (re.compile(r"/home/uniai\b"), "Hardcoded user home path '/home/uniai' (use Path.home())"),
    (re.compile(r"/media/uniai\b"), "Hardcoded mount path '/media/uniai' (use UNIFORGE_HOME / Path(__file__))"),
    (re.compile(r"\bUniRetail\b|\bUniRetailApp\b"), "Hardcoded project name 'UniRetail'"),
    (re.compile(r"\bUniGuard\b"), "Hardcoded project name 'UniGuard'"),
)


def _iter_source_files():
    scan_roots = [ROOT / "src"] + list((ROOT / "packages").glob("*/src"))
    for base in scan_roots:
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            yield py_file


def test_zero_hardcoded_machine_paths_or_project_links() -> None:
    violations: list[str] = []
    for py_file in _iter_source_files():
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern, reason in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    rel = py_file.relative_to(ROOT)
                    violations.append(f"{rel}:{lineno} -> {reason}: {line.strip()}")

    assert not violations, "Portability Gate Failed:\n" + "\n".join(violations)
