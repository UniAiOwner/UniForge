"""
UniExec CLI
===========
Command-line interface for the Sovereign Sandboxed Code Mode Runtime.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from uniexec import __version__
from uniexec.engine import get_engine

app = typer.Typer(
    name="uniexec",
    help="UniExec: Sovereign Sandboxed Code Mode Runtime for UniCortex Brain 2.0",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Display UniExec version."""
    console.print(f"[bold cyan]UniExec[/bold cyan] version [bold green]{__version__}[/bold green] (arXiv:2611.19123)")


@app.command()
def run(
    script_path: Path = typer.Argument(..., help="Path to Python script to execute"),
    timeout: int = typer.Option(15, "--timeout", "-t", help="Execution timeout in seconds")
):
    """Execute an agent script inside the Bubblewrap sandbox."""
    if not script_path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{script_path}' not found.")
        raise typer.Exit(code=1)

    code = script_path.read_text(encoding="utf-8", errors="replace")
    engine = get_engine()

    with console.status(f"[bold cyan]Executing '{script_path.name}' inside isolated sandbox...[/bold cyan]"):
        res = engine.execute(code, timeout_seconds=timeout)

    border = "green" if res.status == "SUCCESS" else "red"
    console.print(Panel(res.to_readable_summary(), title=f"UniExec Sandbox: {script_path.name}", border_style=border))

    if res.status != "SUCCESS":
        raise typer.Exit(code=1)


@app.command(name="eval")
def eval_cmd(
    code: str = typer.Argument(..., help="Python code snippet to execute"),
    timeout: int = typer.Option(15, "--timeout", "-t", help="Execution timeout in seconds")
):
    """Evaluate an inline Python expression or snippet inside the Bubblewrap sandbox."""
    engine = get_engine()
    with console.status("[bold cyan]Evaluating snippet in sandbox...[/bold cyan]"):
        res = engine.execute(code, timeout_seconds=timeout)

    border = "green" if res.status == "SUCCESS" else "red"
    console.print(Panel(res.to_readable_summary(), title="UniExec Inline Eval", border_style=border))

    if res.status != "SUCCESS":
        raise typer.Exit(code=1)


@app.command()
def doctor():
    """Run self-diagnostic checks on Bubblewrap and POSIX limits."""
    console.print("[bold cyan]=== UNIBREAK DOCTOR (Sandbox Self-Diagnostic) ===[/bold cyan]\n")
    engine = get_engine()
    doc = engine.doctor()

    table = Table(title="⬢ UniExec Sandbox Health & Readiness")
    table.add_column("Component", style="bold cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")

    table.add_row(
        "Bubblewrap Binary (bwrap)",
        "[green]PASS[/green]" if doc["bwrap_available"] else "[red]FAIL[/red]",
        doc["bwrap_path"] or "bwrap not found in PATH"
    )
    table.add_row(
        "Resource Limiter (prlimit)",
        "[green]PASS[/green]" if doc["prlimit_available"] else "[red]FAIL[/red]",
        doc["prlimit_path"] or "prlimit not found in PATH"
    )
    table.add_row(
        "Sandbox Micro-Execution",
        "[green]PASS[/green]" if doc["sandbox_micro_execution"] else "[red]FAIL[/red]",
        f"Micro-execution latency: {doc['execution_latency_ms']:.2f}ms"
    )

    console.print(table)
    if doc["is_healthy"]:
        console.print("\n[bold green]✔ UNIBREAK IS 100% HEALTHY & OPERATIONAL[/bold green]")
    else:
        console.print("\n[bold red]❌ UNIBREAK HAS DIAGNOSTIC FAILURES[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def benchmark():
    """Measure Code Mode token savings and execution latency."""
    console.print("[bold cyan]Running Code Mode vs Plain MCP Benchmark...[/bold cyan]\n")
    engine = get_engine()
    bench = engine.benchmark()

    table = Table(title="⚡ Code Mode Efficiency Benchmark (arXiv:2611.19123)")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Execution Latency", f"{bench['execution_time_ms']:.2f} ms")
    table.add_row("Plain MCP Estimated Tokens", f"{bench['plain_mcp_estimated_tokens']} tokens")
    table.add_row("Code Mode Tokens Used", f"{bench['code_mode_tokens']} tokens")
    table.add_row("Net Token Savings", f"{bench['token_savings_percent']}% reduction")

    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
