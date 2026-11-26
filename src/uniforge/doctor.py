"""UniForge Diagnostic Engine.

Audits all 13 sovereign diagnostic pillars across the entire unified suite.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table

console = Console()

SUITE_ROOT = Path(os.environ.get("UNIFORGE_HOME", str(Path(__file__).resolve().parents[2])))
PACKAGES = [
    "unigov", "uniskill", "unimemory", "univerify",
    "uniexec", "unibus", "uniwatch", "triad", "deliberation"
]


def check_packages_integrity() -> Dict[str, Any]:
    """Checks that all 9 packages exist in UniForge/packages."""
    missing = []
    packages_dir = SUITE_ROOT / "packages"
    for pkg in PACKAGES:
        if not (packages_dir / pkg).exists():
            missing.append(pkg)
    if not missing:
        return {
            "name": "UniForge Monorepo Packages (9 Packages)",
            "passed": True,
            "details": f"All 9 packages verified in {packages_dir}",
        }
    return {
        "name": "UniForge Monorepo Packages (9 Packages)",
        "passed": False,
        "details": f"Missing packages: {', '.join(missing)}",
    }


def check_binary_symlinks() -> Dict[str, Any]:
    """Verifies that all binaries are linked in ~/.gemini/antigravity/bin/."""
    ag_bin = Path.home() / ".gemini" / "antigravity" / "bin"
    expected = ["unigov", "uniskill", "unimemory", "univerify", "uniexec", "unibus", "uniwatch", "triad", "deliberate"]
    missing = []
    for b in expected:
        if not (ag_bin / b).exists():
            missing.append(b)
    if not missing:
        return {
            "name": "Global Antigravity Binary Links",
            "passed": True,
            "details": f"All 9 tool binaries linked in {ag_bin}",
        }
    return {
        "name": "Global Antigravity Binary Links",
        "passed": False,
        "details": f"Missing links in {ag_bin}: {', '.join(missing)}",
    }


def run_full_diagnosis() -> bool:
    """Executes the full suite diagnosis and renders a rich status table."""
    from unigov.doctor import diagnose_entire_system
    
    console.print("\n[bold cyan]Running UniForge Sovereign Holistic Suite Diagnosis...[/bold cyan]\n")
    
    checks = [check_packages_integrity(), check_binary_symlinks()]
    checks.extend(diagnose_entire_system())
    
    table = Table(
        title="⬢ UniForge Sovereign Suite Health & Readiness Diagnosis",
        show_header=True,
        header_style="bold magenta",
        title_style="bold cyan",
    )
    table.add_column("Status", width=10, justify="center")
    table.add_column("Diagnostic Pillar", style="bold white", width=40)
    table.add_column("Empirical Details", style="cyan", width=50)

    all_passed = True
    for c in checks:
        if c["passed"]:
            status_text = "[bold green][✓] PASS[/bold green]"
        else:
            status_text = "[bold red][✗] FAIL[/bold red]"
            all_passed = False
        table.add_row(status_text, c["name"], c["details"])

    console.print(table)
    
    if all_passed:
        console.print(f"\n[bold green]ALL {len(checks)} DIAGNOSTIC PILLARS PASSED. UNIFORGE IS 100% HEALTHY & READY.[/bold green]\n")
    else:
        console.print(f"\n[bold red]ATTENTION: SOME PILLARS FAILED AUDIT. REVIEW DETAILS ABOVE.[/bold red]\n")
        
    return all_passed
