"""
UniWatch Typer Command Line Interface.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from uniwatch import __version__
from uniwatch.engine import UniWatchEngine
from uniwatch.watcher import WatcherLoop, audit_file

app = typer.Typer(
    name="uniwatch",
    help="UniWatch: Sovereign Filesystem Inotify Compiler & Syntax Watchdog",
    no_args_is_help=True
)

console = Console()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context, version: bool = typer.Option(False, "--version", "-v", help="Show version")):
    if version:
        console.print(f"[bold cyan]UniWatch[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.command(name="check")
def check(
    path: Path = typer.Argument(..., help="File or directory path to audit"),
):
    """Perform pre-flight syntax, delimiter balance, and invariant audit."""
    p = path.resolve()
    if not p.exists():
        console.print(f"[bold red]✘ Path not found:[/bold red] {p}")
        raise typer.Exit(code=1)

    if p.is_file():
        res = audit_file(p)
        if res.is_passed:
            console.print(f"[bold green]✔ PASS:[/bold green] {p.name} is syntax-balanced and invariant-compliant.")
            if res.warnings:
                for w in res.warnings:
                    console.print(f"  [yellow]⚠ {w}[/yellow]")
            return
        else:
            console.print(f"[bold red]✘ VIOLATIONS FOUND in {p.name}:[/bold red]")
            for err in res.errors:
                console.print(f"  • [red]{err}[/red]")
            raise typer.Exit(code=1)
    else:
        results = UniWatchEngine.check_tree(p)
        violations = [r for r in results if not r.is_passed]
        if not violations:
            console.print(f"[bold green]✔ All monitored files in {p.name} are clean & verified.[/bold green]")
            return

        table = Table(title=f"UniWatch Violations ({len(violations)} files)", show_header=True, header_style="bold red")
        table.add_column("File", style="cyan")
        table.add_column("Violations", style="red")

        for v in violations:
            table.add_row(v.file_path.name, "\n".join(v.errors))
        console.print(table)
        raise typer.Exit(code=1)


@app.command(name="watch")
def watch(
    path: Path = typer.Argument(Path("."), help="Root directory to watch recursively"),
    debounce: int = typer.Option(50, "--debounce", "-d", help="Debounce buffer in milliseconds")
):
    """Start continuous inotify monitoring daemon."""
    p = path.resolve()
    console.print(f"[bold green]Starting UniWatch Daemon on {p} (debounce: {debounce}ms)...[/bold green]")

    def handle_violation(res):
        console.print(f"\n[bold red]⚡ INOTIFY ALERT: Violation in {res.file_path.name}[/bold red]")
        for err in res.errors:
            console.print(f"  • [red]{err}[/red]")

    watcher = WatcherLoop(root_dir=p, debounce_ms=debounce, on_violation=handle_violation)
    try:
        watcher.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping UniWatch daemon...[/yellow]")
        watcher.stop()
        console.print("[bold green]Stopped cleanly.[/bold green]")


@app.command(name="doctor")
def doctor():
    """Diagnose Linux inotify kernel capacity and watchdog health."""
    doc = UniWatchEngine.doctor()
    table = Table(title="UniWatch Diagnostic Report", show_header=True, header_style="bold magenta")
    table.add_column("Subsystem", style="dim")
    table.add_column("Status / Metric")

    status_color = "green" if doc["status"] == "HEALTHY" else "yellow"
    table.add_row("Overall Health", f"[{status_color}]{doc['status']}[/{status_color}]")
    inotify_color = "green" if doc["inotify_available"] else "red"
    table.add_row("Linux inotify (libc.so.6)", f"[{inotify_color}]{'AVAILABLE' if doc['inotify_available'] else 'UNAVAILABLE'}[/{inotify_color}]")
    watches_color = "green" if doc["kernel_capacity_sufficient"] else "yellow"
    table.add_row("Max User Watches", f"[{watches_color}]{doc['max_user_watches']:,}[/{watches_color}] ({'/proc/sys/fs/inotify/max_user_watches'})")

    console.print(table)


@app.command(name="status")
def status():
    """Show brief watchdog status overview."""
    st = UniWatchEngine.status()
    console.print(Panel(
        f"[bold]Linux inotify Available:[/bold] {'Yes' if st['inotify_available'] else 'No'}\n"
        f"[bold]Kernel Watch Capacity:[/bold] {st['max_user_watches']:,}\n"
        f"[bold]Watchdog Health:[/bold] {st['status']}",
        title="UniWatch Status",
        border_style="cyan"
    ))


def main():
    app()


if __name__ == "__main__":
    main()
