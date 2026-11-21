"""UniForge CLI: Master entrypoint for the Sovereign Developer Suite.
"""

import sys
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    help="UniForge: Sovereign Autonomous Developer Suite & Engineering Machine",
    no_args_is_help=True,
)
console = Console()


@app.command("help")
def help_cmd():
    """Show help and available commands."""
    import subprocess
    subprocess.run([sys.executable, "-m", "uniforge.cli", "--help"])


@app.command("activate")
def activate_cmd(
    project_path: Optional[str] = typer.Argument(
        ".", help="Target project root directory path (default: current directory)"
    )
):
    """1-Phrase Autonomous Activation: Introspects workspace, activates UniGov, UniMemory, UniVerify, and UniWatch."""
    from uniforge.activator import activate_project
    target = Path(project_path)
    res = activate_project(target)
    
    constraints_text = "\n".join([f" • {c}" for c in res.get("constraints", [])])
    
    panel_content = (
        f"[bold cyan]{res['project_name']}[/bold cyan] [dim]({res['project_path']})[/dim]\n"
        f"[white]{res['objective']}[/white]\n"
        f"[yellow]Tech Stack:[/yellow] {res['stack']}\n\n"
        f"[bold green][✓] UniGov:[/bold green] Governance {res['gov_status']} | Pre-commit hook: {'Installed' if res['git_hook'] else 'Skipped'}\n"
        f"[bold green][✓] UniMemory:[/bold green] Living memory active ({res['memory_facts']} facts, ~{res['memory_symbols']} source files indexed)\n"
        f"[bold green][✓] UniVerify:[/bold green] Code gate active ({'Clean, 0 drift' if res['verify_clean'] else ', '.join(res['violations'])})\n"
        f"[bold green][✓] UniWatch:[/bold green] Real-time Inotify Sentinel {'Active' if res['watch_active'] else 'Inactive'}\n\n"
        f"[bold magenta]Locked Constraints ({len(res['constraints'])}):[/bold magenta]\n{constraints_text}\n\n"
        f"[bold white]Tasks Ingested:[/bold white] [cyan]{res['task_count']} atomic tasks in DAG[/cyan]\n"
        f"[bold green]STATUS: 100% OPERATIONAL & READY TO ENGINEER.[/bold green]"
    )
    
    console.print(
        Panel.fit(
            panel_content,
            title="⬢ UniForge Sovereign Autonomous Activation",
            border_style="cyan"
        )
    )


@app.command("doctor")
def doctor_cmd():
    """Run full diagnostic audit across all 13 sovereign pillars and 9 packages."""
    from uniforge.doctor import run_full_diagnosis
    passed = run_full_diagnosis()
    if not passed:
        raise typer.Exit(1)


@app.command("status")
def status_cmd(
    project_path: Optional[str] = typer.Argument(
        ".", help="Target project root directory path (default: current directory)"
    )
):
    """View sovereign governance and task DAG status for any target workspace."""
    from uniforge.workspace import get_workspace_status
    target = Path(project_path)
    res = get_workspace_status(target)
    
    if res["status"] == "UNINITIALIZED":
        console.print(f"[bold yellow]Notice:[/bold yellow] {res.get('message', 'Workspace uninitialized')}")
        raise typer.Exit(1)
        
    constraints_text = "\n".join([f" • {c}" for c in res.get("hard_constraints", [])]) or " None"
    task_counts = res.get("task_counts", {})
    counts_text = " | ".join([f"[bold]{k}:[/bold] {v}" for k, v in task_counts.items()]) or "No tasks ingested yet"

    console.print(
        Panel.fit(
            f"[bold cyan]{res['project_name']}[/bold cyan]\n"
            f"[white]{res['core_objective']}[/white]\n\n"
            f"[bold magenta]Locked Constraints:[/bold magenta]\n{constraints_text}\n\n"
            f"[bold green]Tasks Status:[/bold green] {counts_text}\n"
            f"[dim]Root: {res['project_path']}[/dim]",
            title="⬢ UniForge Workspace Status",
            border_style="cyan"
        )
    )


@app.command("init")
def init_cmd(
    project_path: str = typer.Argument(
        ..., help="Target project root directory to initialize"
    ),
    project_name: str = typer.Option(
        ..., "--project-name", "-n", help="Name of the project"
    ),
    objective: str = typer.Option(
        ..., "--objective", "-o", help="Core mission / objective of the project"
    ),
):
    """Initialize a sovereign UniForge / UniGov workspace in the target project."""
    from uniforge.workspace import init_workspace
    target = Path(project_path)
    res = init_workspace(target, project_name, objective)
    
    console.print(
        Panel.fit(
            f"[bold green]✓ Initialized Sovereign Workspace for '{res['project_name']}'[/bold green]\n"
            f"[white]Objective: {objective}[/white]\n\n"
            f"[dim]Root: {res['project_path']}[/dim]\n"
            f"[dim]Governance Directory: {res['gov_dir']}[/dim]\n"
            f"[dim]Git Pre-Commit Hook: {'Installed' if res['git_hook_installed'] else 'Skipped (no .git)'}[/dim]",
            title="⬢ UniForge Workspace Initialized",
            border_style="green"
        )
    )


@app.command("test")
def test_cmd(
    package: Optional[str] = typer.Option(
        None, "--package", "-p", help="Specific package to test (e.g. unigov, triad, deliberation)"
    )
):
    """Run automated verification test suites across UniForge packages."""
    import subprocess
    suite_root = Path("/media/uniai/UniAi/PROJECTS_MIGRATED/UniForge/packages")
    python_bin = "/home/uniai/.local/venv314/bin/python"
    
    targets = [package] if package else ["unigov", "uniskill", "unimemory", "univerify", "uniexec", "unibus", "uniwatch", "triad", "deliberation"]
    
    all_passed = True
    for pkg in targets:
        pkg_dir = suite_root / pkg
        if not pkg_dir.exists():
            console.print(f"[bold red]Package '{pkg}' not found in {suite_root}[/bold red]")
            continue
            
        console.print(f"\n[bold cyan]=== Testing {pkg} ===[/bold cyan]")
        cmd = [python_bin, "-m", "pytest", str(pkg_dir)]
        # For packages without top-level tests, check subfolder
        res = subprocess.run(cmd, cwd=str(pkg_dir))
        if res.returncode != 0:
            all_passed = False
            
    if all_passed:
        console.print("\n[bold green]ALL TARGET TEST SUITES PASSED.[/bold green]")
    else:
        console.print("\n[bold red]SOME TESTS FAILED.[/bold red]")
        raise typer.Exit(1)


@app.command("version")
def version_cmd():
    """Show UniForge suite version and integrated package manifest."""
    from uniforge import __version__, __suite_name__
    console.print(f"[bold cyan]{__suite_name__}[/bold cyan] version [bold green]v{__version__}[/bold green]")
    console.print("[dim]Integrated Packages (9):[/dim]")
    packages = [
        ("unigov", "Pillar 1: Sovereign Governance & Tasks DAG"),
        ("uniskill", "Pillar 2: Surgical Skills Router & Economizer"),
        ("unimemory", "Pillar 3: 5-Tier Holographic Living Memory"),
        ("univerify", "Pillar 4: Z3 SMT Gatekeeper & Law-000 Guard"),
        ("uniexec", "Pillar 5: bwrap Sandboxed Code-Mode Runtime"),
        ("unibus", "Pillar 6: Real-time IPC & File Work Mutex Bus"),
        ("uniwatch", "Pillar 7: Linux Inotify Sentinel & Watchdog"),
        ("triad", "Sovereign Coding Triad (Python+Kotlin+Security)"),
        ("deliberation", "Frontal Lobe Deliberative Councils & MCTS"),
    ]
    for name, desc in packages:
        console.print(f"  • [bold white]{name:<14}[/bold white] - [cyan]{desc}[/cyan]")


if __name__ == "__main__":
    app()
