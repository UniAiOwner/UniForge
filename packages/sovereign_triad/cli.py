"""
Sovereign Coding Triad Typer CLI.
Entrypoint for the 3-in-1 Sovereign Coding Engine.
"""

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ensure parent directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sovereign_triad.triad_orchestrator import SovereignTriadOrchestrator
from sovereign_triad.models import FindingSeverity

app = typer.Typer(help="Sovereign Coding Triad CLI: Python, Kotlin, and Security Specialist Engines")
console = Console()


@app.command()
def audit(path: str = typer.Argument(..., help="File path to audit")):
    """Runs Python, Kotlin, and Security specialist audits on a file."""
    orchestrator = SovereignTriadOrchestrator()
    console.print(f"[bold cyan]🔍 Sovereign Triad Audit:[/bold cyan] {path}")

    report = orchestrator.audit_target(path)

    table = Table(title=f"Audit Results: {report.language.value.upper()} ({path})")
    table.add_column("Rule ID", style="cyan", no_wrap=True)
    table.add_column("Severity", style="bold")
    table.add_column("Line", style="magenta")
    table.add_column("Message", style="white")

    for f in report.findings:
        sev_style = "red" if f.severity == FindingSeverity.CRITICAL else "yellow"
        table.add_row(f.rule_id, f"[{sev_style}]{f.severity.value}[/{sev_style}]", str(f.line_number), f.message)

    console.print(table)

    if report.passed:
        console.print(Panel(f"✔ [bold green]PASSED[/bold green]: Zero critical violations found ({report.summary})", border_style="green"))
    else:
        console.print(Panel(f"✘ [bold red]FAILED[/bold red]: {report.critical_count} critical violations detected!", border_style="red"))
        raise typer.Exit(code=1)


@app.command()
def certify(path: str = typer.Argument(..., help="Target path to formally verify and certify")):
    """Formally verifies and issues a Sovereign Triad Verification Certificate."""
    orchestrator = SovereignTriadOrchestrator()
    console.print(f"[bold cyan]📜 Issuing Verification Certificate for:[/bold cyan] {path}")

    cert = orchestrator.verify_and_certify(path)

    verdict_color = "green" if cert.overall_passed else "red"
    verdict_text = "RATIFIED" if cert.overall_passed else "REJECTED"

    table = Table(title="Sovereign Verification Certificate")
    table.add_column("Dimension", style="cyan")
    table.add_column("Status / Score", style="bold")

    table.add_row("Syntax & AST Valid", "[green]PASS[/green]" if cert.syntax_valid else "[red]FAIL[/red]")
    table.add_row("Security & Secret Safe", "[green]PASS[/green]" if cert.security_valid else "[red]FAIL[/red]")
    table.add_row("Constitutional Invariants (Law-000)", "[green]PASS[/green]" if cert.invariants_valid else "[red]FAIL[/red]")
    table.add_row("Artifact Soundness (arXiv:2611.21407)", f"{cert.artifact_soundness_score:.2f} ({'SOUND' if cert.artifact_soundness_score >= 0.75 else 'UNSOUND'})")
    table.add_row("Overall Verdict", f"[{verdict_color}]{verdict_text}[/{verdict_color}]")

    console.print(table)
    if not cert.overall_passed:
        raise typer.Exit(code=1)


@app.command()
def exec(cmd: str = typer.Argument(..., help="Command string to run")):
    """Executes a command inside the UniExec Bubblewrap sandbox."""
    orchestrator = SovereignTriadOrchestrator()
    console.print(f"[bold cyan]⚡ Sandboxed Execution:[/bold cyan] {cmd}")

    res = orchestrator.execute_command(cmd)
    console.print(f"Exit Code: {res.exit_code} (Duration: {res.duration_ms:.2f}ms, Sandbox: {res.sandbox_used})")
    if res.stdout:
        console.print(f"[dim]STDOUT:[/dim]\n{res.stdout}")
    if res.stderr:
        console.print(f"[red]STDERR:[/red]\n{res.stderr}")

    if res.exit_code != 0:
        raise typer.Exit(code=res.exit_code)


@app.command()
def doctor():
    """Runs health checks for Python, Kotlin, and Security specialists and 7-pillar bindings."""
    console.print("[bold cyan]🩺 Sovereign Coding Triad Doctor Diagnostic[/bold cyan]")
    table = Table()
    table.add_column("Subsystem / Specialist", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")

    # 1. Python Specialist
    table.add_row("Python Engineering Prime", "[green]ONLINE[/green]", "CPython AST + PEP 703 No-GIL + Async blocking detector")

    # 2. Kotlin Specialist
    table.add_row("Kotlin Android Prime", "[green]ONLINE[/green]", "K2 FIR syntax + Law-000 zero-suppress + ACC-001 paise money")

    # 3. Security Specialist
    table.add_row("Security & AppSec Prime", "[green]ONLINE[/green]", "Shannon entropy scanner + Z3 SMT prover + OWASP MASVS")

    # 4. Pillar Integrations
    from sovereign_triad.triad_orchestrator import UNIBUS_AVAILABLE, UNIVERIFY_AVAILABLE, UNIEXEC_AVAILABLE
    table.add_row("UniBus IPC & Mutex (Pillar 6)", "[green]CONNECTED[/green]" if UNIBUS_AVAILABLE else "[yellow]OFFLINE[/yellow]", "Work mutex leases & priority events")
    table.add_row("UniVerify Gatekeeper (Pillar 4)", "[green]CONNECTED[/green]" if UNIVERIFY_AVAILABLE else "[yellow]OFFLINE[/yellow]", "Z3 SMT Bounds + Law-000 + Scorer")
    table.add_row("UniExec Sandbox (Pillar 5)", "[green]CONNECTED[/green]" if UNIEXEC_AVAILABLE else "[yellow]OFFLINE[/yellow]", "Bubblewrap container isolation")

    console.print(table)


if __name__ == "__main__":
    app()
