"""
UniVerify CLI
=============
Command-line interface for the Sovereign Code & Systems Verification Gate.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from univerify import __version__
from univerify.gatekeeper import Gatekeeper
from univerify.z3_prover import FormalZ3Prover
from univerify.invariants import InvariantGuard
from univerify.artifact_scorer import DeterministicArtifactScorer

app = typer.Typer(
    name="univerify",
    help="Sovereign Code & Invariant Verification Gatekeeper for UniCortex Brain 2.0",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Display UniVerify version."""
    console.print(f"[bold cyan]UniVerify[/bold cyan] version [bold green]{__version__}[/bold green]")


@app.command()
def gate(
    file_path: Path = typer.Argument(..., help="Path to code file to verify"),
    test_path: Optional[str] = typer.Option(None, "--test", "-t", help="Optional pytest suite path")
):
    """Run full 4-level verification gatekeeper on a target code file."""
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist.")
        raise typer.Exit(code=1)

    gk = Gatekeeper()
    with console.status(f"[bold cyan]Verifying code '{file_path.name}' through 4-tier gate...[/bold cyan]"):
        res = gk.verify_file(str(file_path), test_path=test_path)

    console.print(Panel(res.to_readable_summary(), title=f"UniVerify Code Gate: {file_path.name}", border_style="green" if res.is_passed else "red"))

    if not res.is_passed:
        raise typer.Exit(code=1)


@app.command()
def scan_code(
    file_path: Path = typer.Argument(..., help="Path to code file to scan for invariant violations")
):
    """Fast scan for Law-000 @Suppress, fake passes, secret leaks, and unsafe execution."""
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist.")
        raise typer.Exit(code=1)

    code = file_path.read_text(encoding="utf-8", errors="replace")
    guard = InvariantGuard()
    res = guard.check_code(code, filename=file_path.name)

    if res.passed:
        console.print(f"[bold green]✔ CLEAN:[/bold green] No invariant or security violations in '{file_path.name}'.")
    else:
        console.print(f"[bold red]❌ VIOLATIONS FOUND ({len(res.violations)}):[/bold red]")
        for v in res.violations:
            loc = f":{v.line_number}" if v.line_number else ""
            console.print(f"  • [{v.severity}] {v.rule_name}{loc}: {v.explanation}")
        raise typer.Exit(code=1)


@app.command()
def prove_loop(
    max_iterations: int = typer.Argument(..., help="Maximum loop/retry iterations bound"),
    step: int = typer.Option(1, "--step", "-s", help="Step decrement/increment per cycle")
):
    """Formally prove algorithmic loop termination using Z3 SMT solver."""
    prover = FormalZ3Prover()
    res = prover.prove_loop_termination(max_iterations, decrement_step=step)

    if res.is_satisfied:
        console.print(f"[bold green]✔ PROVEN:[/bold green] {res.mathematical_rationale}")
    else:
        console.print(f"[bold red]❌ REFUTED:[/bold red] {res.mathematical_rationale} | Counter-example: {res.counter_example}")
        raise typer.Exit(code=1)


@app.command()
def prove_bounds(
    buffer_size: int = typer.Argument(..., help="Allocated buffer/array size"),
    min_index: int = typer.Argument(..., help="Minimum possible access index"),
    max_index: int = typer.Argument(..., help="Maximum possible access index")
):
    """Formally prove array/buffer index bounds safety (0 <= idx < size) using Z3."""
    prover = FormalZ3Prover()
    res = prover.prove_buffer_index_bounds(buffer_size, min_index, max_index)

    if res.is_satisfied:
        console.print(f"[bold green]✔ PROVEN:[/bold green] {res.mathematical_rationale}")
    else:
        console.print(f"[bold red]❌ VIOLATION:[/bold red] {res.mathematical_rationale} | Counter-example: {res.counter_example}")
        raise typer.Exit(code=1)


@app.command()
def score(
    file_path: Path = typer.Argument(..., help="Source code file to score")
):
    """Calculate deterministic physical artifact score (arXiv:2611.21407)."""
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist.")
        raise typer.Exit(code=1)

    content = file_path.read_text(encoding="utf-8", errors="replace")
    scorer = DeterministicArtifactScorer()
    res = scorer.score_code_artifact(content, filename=file_path.name)

    table = Table(title=f"Deterministic Physical Artifact Score: {file_path.name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", style="magenta")

    table.add_row("Total Score", f"{res.total_score:.3f} / 1.000")
    table.add_row("Soundness Gate (>= 0.75)", "[bold green]SOUND[/bold green]" if res.is_sound else "[bold red]UNSOUND[/bold red]")
    table.add_row("AST Syntax", f"{res.syntax_score:.3f}")
    table.add_row("Structured Invariants", f"{res.invariant_score:.3f}")
    table.add_row("Evidence & Tests", f"{res.evidence_score:.3f}")
    table.add_row("Discipline", f"{res.literature_score:.3f}")

    console.print(table)
    if res.failure_reasons:
        console.print("[yellow]Notes / Failure Reasons:[/yellow]")
        for fr in res.failure_reasons:
            console.print(f"  • {fr}")

    if not res.is_sound:
        raise typer.Exit(code=1)


@app.command()
def doctor():
    """Run self-diagnostic checks on UniVerify code verification components."""
    console.print("[bold cyan]=== UNIVERIFY DOCTOR (Self-Diagnostic) ===[/bold cyan]")
    all_ok = True

    # 1. Z3 SMT Theorem Prover Check
    try:
        prover = FormalZ3Prover()
        res = prover.prove_buffer_index_bounds(100, 0, 99)
        if res.is_satisfied:
            console.print("  ✔ [bold green]Z3 SMT Theorem Prover:[/bold green] Operational (Formal bounds proof in sub-ms)")
        else:
            console.print("  ❌ [bold red]Z3 SMT Theorem Prover:[/bold red] Micro-proof failed!")
            all_ok = False
    except Exception as e:
        console.print(f"  ❌ [bold red]Z3 SMT Solver Error:[/bold red] {e}")
        all_ok = False

    # 2. Invariant Code Guard Check
    try:
        guard = InvariantGuard()
        chk = guard.check_code("fun compute(): Int = 42", filename="test.kt")
        if chk.passed:
            console.print("  ✔ [bold green]Level 1 Invariant Code Guard:[/bold green] Operational")
        else:
            console.print("  ❌ [bold red]Level 1 Invariant Code Guard:[/bold red] Check failed!")
            all_ok = False
    except Exception as e:
        console.print(f"  ❌ [bold red]Level 1 Invariant Code Guard Error:[/bold red] {e}")
        all_ok = False

    # 3. Artifact Scorer Check
    try:
        scorer = DeterministicArtifactScorer()
        sample_code = '"""Calculates sum."""\ndef add(a: int, b: int) -> int:\n    assert a >= 0\n    return a + b\n'
        sc = scorer.score_code_artifact(sample_code, filename="math.py")
        if sc.is_sound:
            console.print("  ✔ [bold green]Level 3 Artifact Scorer:[/bold green] Operational (arXiv:2611.21407)")
        else:
            console.print("  ❌ [bold red]Level 3 Artifact Scorer:[/bold red] Sample scoring failed!")
            all_ok = False
    except Exception as e:
        console.print(f"  ❌ [bold red]Level 3 Artifact Scorer Error:[/bold red] {e}")
        all_ok = False

    if all_ok:
        console.print("\n[bold green]✔ UniVerify is 100% healthy and operational for Code Verification![/bold green]")
    else:
        console.print("\n[bold red]❌ UniVerify has diagnostic failures![/bold red]")
        raise typer.Exit(code=1)


def main():
    app()


if __name__ == "__main__":
    main()
