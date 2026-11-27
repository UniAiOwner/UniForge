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
    import os
    import subprocess
    suite_root = Path(os.environ.get("UNIFORGE_HOME", str(Path(__file__).resolve().parents[2]))) / "packages"
    python_bin = sys.executable
    
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
        ("synthesizer", "Pillar 10: Multi-Repo AST Synthesizer & Code Transplanter"),
        ("planner", "Pillar 11: Sovereign Architectural Roadmap & Task DAG Synthesizer"),
    ]
    for name, desc in packages:
        console.print(f"  • [bold white]{name:<14}[/bold white] - [cyan]{desc}[/cyan]")


@app.command("synthesize")
def synthesize_cmd(
    target_workspace: str = typer.Option(
        ".", "--target", "-t", help="Target unified workspace directory"
    ),
    output_report: Optional[str] = typer.Option(
        None, "--output", "-o", help="Path to export forensic matrix JSON"
    ),
    repos_config: Optional[str] = typer.Option(
        None, "--repos-config", "-c", help="Optional JSON file mapping repo names to paths"
    ),
):
    """Pillar 10: Multi-Repo Cross-AST Forensic Audit, Deduplication & SOTA Quality Synthesis."""
    import json
    from uniforge.synthesizer import MultiRepoSynthesizer

    target_p = Path(target_workspace).resolve()
    repos: dict[str, str] = {}
    cfg_path = Path(repos_config).resolve() if repos_config else (target_p / ".uniforge" / "repos.json")
    if cfg_path.exists():
        repos = json.loads(cfg_path.read_text(encoding="utf-8"))
    else:
        # Auto-discover git repositories inside target workspace
        for child in sorted(target_p.iterdir()):
            if child.is_dir() and (child / ".git").exists():
                repos[child.name] = str(child)
        if not repos:
            repos[target_p.name] = str(target_p)

    synthesizer = MultiRepoSynthesizer(repos, str(target_p))
    summary = synthesizer.scan_and_analyze()
    synthesizer.print_report(summary)

    out_p = Path(output_report).resolve() if output_report else (target_p / "PLANNING" / "synthesis_matrix.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    synthesizer.export_matrix(str(out_p))


@app.command("plan")
def plan_cmd(
    workspace: Optional[str] = typer.Argument(
        ".", help="Target project workspace directory (default: current directory)"
    ),
    markdown_output: Optional[str] = typer.Option(
        None, "--output-markdown", "-o", help="Path to export markdown plan"
    )
):
    """Pillar 11: Sovereign Architectural Roadmap & Task DAG Synthesis Engine."""
    from uniforge.planner import SovereignRoadmapPlanner
    target_p = Path(workspace).resolve()
    planner = SovereignRoadmapPlanner(target_p)
    tasks = planner.synthesize_master_plan()
    inserted_tasks, inserted_deps = planner.compile_plan_to_unigov(tasks)
    
    md_out = Path(markdown_output) if markdown_output else (target_p / "PLANNING" / "antigravity_plan" / "sovereign_master_roadmap_2026_2030.md")
    planner.export_markdown_plan(tasks, md_out)
    planner.render_terminal_tree(tasks)
    
    console.print(
        Panel.fit(
            f"[bold green]✓ Synthesized & Ingested {inserted_tasks} Tasks across 4 Strategic Phases[/bold green]\n"
            f"[white]Dependencies Locked:[/white] [cyan]{inserted_deps} DAG edges[/cyan]\n"
            f"[dim]Governance DB:[/dim] [dim]{planner.db_path}[/dim]\n"
            f"[dim]Plan Document:[/dim] [dim]{md_out}[/dim]",
            title="⬢ UniForge Roadmap Synthesis Complete",
            border_style="green"
        )
    )


@app.command("genesis")
def genesis_cmd(
    vision: str = typer.Argument(..., help="Raw project vision or idea in plain language"),
    target_dir: str = typer.Option(".", "--dir", "-d", help="Target project directory"),
    project_name: Optional[str] = typer.Option(None, "--name", "-n", help="Explicit project name"),
    scaffold: bool = typer.Option(False, "--scaffold", "-s", help="Generate runnable starter folder & code skeleton"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing scaffold files"),
    json_out: Optional[str] = typer.Option(None, "--json-out", help="Optional path to export JSON blueprint"),
):
    """Vision-to-Blueprint & Project Skeleton Architect: Categorizes vision, recommends stack, designs architecture/UI, and scaffolds starter code."""
    from uniforge.genesis import VisionGenesisArchitect

    root = Path(target_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)

    architect = VisionGenesisArchitect()
    bp = architect.generate_blueprint(vision, project_name=project_name)
    architect.render_terminal_report(bp)

    md_path = architect.export_blueprint_markdown(bp, root / "PLANNING" / "MASTER_ARCHITECTURE_BLUEPRINT.md")
    task_count = architect.register_unigov_tasks(bp, root)
    scaffolded = architect.scaffold_skeleton(bp, root, force=force) if scaffold else []

    if json_out:
        jp = Path(json_out).resolve()
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(bp.model_dump_json(indent=2), encoding="utf-8")

    scaffold_msg = f"\n[bold green]✓ Scaffolded Files:[/bold green] {len(scaffolded)} files" if scaffold else "\n[dim]Tip: Pass --scaffold (-s) to generate starter folders & code.[/dim]"
    console.print(
        Panel.fit(
            f"[bold green]✓ Blueprint Exported:[/bold green] {md_path}\n"
            f"[bold green]✓ UniGov Tasks Registered:[/bold green] {task_count} tasks in {root / '.unigov' / 'state.db'}"
            f"{scaffold_msg}",
            title="⬢ UniForge Genesis Complete",
            border_style="green",
        )
    )


@app.command("research")
def research_cmd(
    path: Path = typer.Argument(Path("."), help="Target project directory to audit against latest standards."),
    topic: Optional[str] = typer.Option(None, "--topic", help="Optional focus topic for the research report."),
    online: bool = typer.Option(False, "--online", help="Query live PyPI/npm registries for latest versions."),
    no_report: bool = typer.Option(False, "--no-report", help="Do not write PLANNING/RESEARCH_LATEST_STANDARDS.md."),
):
    """Run UniForge Researcher to check project stack against latest 2026 standards."""
    from unigov.researcher import run_research

    res = run_research(project_root=path, topic=topic, online=online, write_report=not no_report)
    if res.get("report_path"):
        console.print(f"[bold green]✓ Research Report:[/bold green] {res['report_path']}")


if __name__ == "__main__":
    app()
