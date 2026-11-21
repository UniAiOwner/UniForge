"""
UniMemory CLI
=============
Command line interface for the UniMemory Substrate.
"""

import sys
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from unimemory.engine import get_engine
from unimemory.migrator import migrate_legacy_databases

app = typer.Typer(help="UniMemory: Sovereign Cognitive Memory Substrate CLI", no_args_is_help=True)
console = Console()


@app.command()
def recall(
    query: str = typer.Argument(..., help="Query text to search across memory tiers"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Scope recall to specific project"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Maximum results per tier"),
):
    """Sub-millisecond multi-tier hybrid memory recall."""
    engine = get_engine()
    res = engine.recall(query=query, project_scope=project, top_k=top_k)
    console.print(Panel(res.to_readable_summary(), title="🧠 UniMemory Recall Engine", border_style="cyan"))


@app.command()
def store(
    subject: str = typer.Argument(..., help="Subject entity"),
    predicate: str = typer.Argument(..., help="Relationship or predicate"),
    target_object: str = typer.Argument(..., help="Target object or concept"),
    confidence: float = typer.Option(1.0, "--confidence", "-c", help="Confidence score 0.0-1.0"),
):
    """Store a bi-temporal semantic fact into the knowledge graph."""
    engine = get_engine()
    fact = engine.store_fact(subject=subject, predicate=predicate, target_object=target_object, confidence=confidence)
    console.print(f"[green]✔ Stored Fact:[/green] {fact['subject']} --[{fact['predicate']}]--> {fact['object']} (ID: {fact['fact_id']})")


@app.command()
def episode(
    project: str = typer.Argument(..., help="Project name"),
    goal: str = typer.Argument(..., help="Task goal or milestone"),
    lesson: str = typer.Argument(..., help="Root cause takeaway / Law-STARK countermeasure"),
    status: str = typer.Option("SUCCESS", "--status", "-s", help="SUCCESS, FAILED, or PARTIAL"),
):
    """Record an episodic execution trace for Law-STARK repeat blocking."""
    engine = get_engine()
    ep = engine.record_episode(
        project=project,
        goal=goal,
        steps_taken=[goal],
        errors_encountered=[],
        root_cause_lesson=lesson,
        status=status
    )
    console.print(f"[green]✔ Recorded Episode:[/green] [{ep['status']}] {ep['project']}: {ep['goal']} (ID: {ep['episode_id']})")


@app.command()
def working(
    key: str = typer.Argument(..., help="Context variable name"),
    value: str = typer.Argument(..., help="JSON or text value"),
    project: str = typer.Option("GLOBAL", "--project", "-p", help="Project scope"),
    priority: int = typer.Option(1, "--priority", help="Priority 1-3"),
):
    """Store an active working context key-value item."""
    engine = get_engine()
    item = engine.set_working(key=key, value=value, project_scope=project, priority=priority)
    console.print(f"[green]✔ Stored Working Context:[/green] {item['key']} = {item['value_json']}")


@app.command()
def sync(
    project_path: str = typer.Argument(..., help="Path to project directory"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name override"),
):
    """Index codebase symbols and AST elements into the VFS map."""
    engine = get_engine()
    res = engine.sync_project(project_path=Path(project_path), project_name=name)
    if res["status"] == "SUCCESS":
        console.print(f"[green]✔ Project Synced:[/green] {res['project']} ({res['symbols_indexed']} symbols from {res['files_scanned']} files)")
    else:
        console.print(f"[red]❌ Sync Failed:[/red] {res.get('error')}")


@app.command()
def migrate(
    legacy_dir: str = typer.Option(
        "/media/uniai/UniAi/PROJECTS_MIGRATED/Agentic team/02_UCMF_MEMORY",
        "--source", "-s",
        help="Path to legacy 02_UCMF_MEMORY directory"
    ),
):
    """Migrate facts and decisions from fragmented databases into ~/.unicortex/brain_memory.db."""
    console.print(f"Starting historical migration from: {legacy_dir}...")
    res = migrate_legacy_databases(legacy_dir=Path(legacy_dir))
    console.print(f"[green]✔ Migration Complete![/green] Facts: {res['migrated_facts']}, Episodes: {res['migrated_episodes']}")
    if res.get("errors"):
        console.print(f"[yellow]Warnings:[/yellow] {res['errors']}")


@app.command()
def doctor():
    """Run comprehensive health checks on the UniMemory Substrate."""
    engine = get_engine()
    doc = engine.doctor()

    table = Table(title="⬢ UniMemory Substrate Health & Telemetry")
    table.add_column("Metric / Check", style="cyan")
    table.add_column("Value", style="green" if doc["is_healthy"] else "red")

    table.add_row("Database Path", doc["database_path"])
    table.add_row("SQLite Integrity", doc["integrity_check"].upper())
    table.add_row("Working Context Count", str(doc["working_context_count"]))
    table.add_row("Episodic Records Count", str(doc["episodic_records_count"]))
    table.add_row("Active Semantic Facts", str(doc["active_semantic_facts_count"]))
    table.add_row("Indexed Codebase Symbols", str(doc["indexed_symbols_count"]))
    table.add_row("FTS5 Indexed Documents", str(doc["fts5_indexed_documents"]))

    console.print(table)
    if doc["is_healthy"]:
        console.print("[bold green]✔ UNIMEMORY IS 100% HEALTHY & READY[/bold green]")
    else:
        console.print("[bold red]❌ UNIMEMORY INTEGRITY CHECK FAILED[/bold red]")


@app.command()
def status():
    """Display quick summary of active working memory, recent episodes, and living beacon."""
    engine = get_engine()
    active_working = engine.working.list_active(limit=5)
    recent_episodes = engine.episodic.list_recent(limit=5)
    beacon = engine.get_beacon()

    console.print(f"\n[bold yellow]{engine.beacon_header()}[/bold yellow]")

    console.print("\n[bold cyan]📌 Active Working Context:[/bold cyan]")
    if not active_working:
        console.print("  (Empty)")
    for w in active_working:
        console.print(f"  • {w.key} = {w.value_json[:80]} (Scope: {w.project_scope})")

    console.print("\n[bold cyan]📜 Recent Episodic Lessons (Law-STARK):[/bold cyan]")
    if not recent_episodes:
        console.print("  (Empty)")
    for ep in recent_episodes:
        console.print(f"  • [{ep.status}] {ep.project}: {ep.goal} -> {ep.root_cause_lesson[:80]}")


# ==============================================================================
# Beacon Sub-Commands
# ==============================================================================
beacon_app = typer.Typer(help="Living Cognitive Light Beacon (Active Mission Anchor & Anti-Drift Sentinel)")
app.add_typer(beacon_app, name="beacon")


@beacon_app.command(name="show")
def beacon_show():
    """Display currently active Cognitive Beacon."""
    engine = get_engine()
    beacon = engine.get_beacon()

    if not beacon:
        console.print("[yellow]No active Cognitive Beacon currently anchored.[/yellow]")
        console.print("Run [bold cyan]unimemory beacon set[/bold cyan] to anchor a new mission.")
        return

    table = Table(title="🚨 Living Cognitive Light Beacon (True North Anchor)")
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Mission Name", beacon.mission_name)
    table.add_row("Parent Goal", beacon.parent_goal)
    table.add_row("Active Milestone", beacon.active_milestone)
    table.add_row("Status", f"[bold green]{beacon.status}[/bold green]")
    table.add_row("In-Scope Paths", "\n".join(beacon.in_scope_paths) if beacon.in_scope_paths else "(All)")
    table.add_row("Forbidden Domains", ", ".join(beacon.forbidden_domains) if beacon.forbidden_domains else "(None)")
    table.add_row("Ambient Header", beacon.to_ambient_header())

    console.print(table)


@beacon_app.command(name="set")
def beacon_set(
    mission: str = typer.Argument(..., help="High-level Mission Name (e.g. 'UniCortex Brain 2.0')"),
    parent_goal: str = typer.Argument(..., help="Root Parent Goal"),
    milestone: str = typer.Argument(..., help="Current Active Milestone (e.g. 'Pillar 5: UniExec')"),
    in_scope: Optional[str] = typer.Option(None, "--in-scope", help="Comma-separated path globs allowed to mutate"),
    forbidden: Optional[str] = typer.Option(None, "--forbidden", help="Comma-separated forbidden domain keywords"),
):
    """Anchor a new Cognitive Beacon mission."""
    engine = get_engine()
    in_scope_list = [p.strip() for p in in_scope.split(",") if p.strip()] if in_scope else []
    forbidden_list = [f.strip() for f in forbidden.split(",") if f.strip()] if forbidden else []

    b = engine.set_beacon(
        mission_name=mission,
        parent_goal=parent_goal,
        active_milestone=milestone,
        in_scope_paths=in_scope_list,
        forbidden_domains=forbidden_list
    )
    console.print(f"[bold green]✔ Cognitive Beacon Anchored & Activated![/bold green]")
    console.print(f"Header: [bold yellow]{b.to_ambient_header()}[/bold yellow]")


@beacon_app.command(name="check")
def beacon_check(
    target_path: Optional[str] = typer.Option(None, "--path", "-p", help="Target file path to check"),
    intent: str = typer.Option("", "--intent", "-i", help="Action intent summary text"),
):
    """Verify if an action or file path deviates from the active beacon mission."""
    engine = get_engine()
    res = engine.check_drift(target_path=target_path, intent_summary=intent)
    if res.allowed:
        console.print("[bold green]✔ ALIGNED:[/bold green] Action is in-scope with active beacon.")
    else:
        console.print(f"[bold red]⛔ DRIFT BLOCKED:[/bold red] {res.violation_reason}")
        raise typer.Exit(code=1)


@beacon_app.command(name="complete")
def beacon_complete():
    """Mark the active beacon as COMPLETED upon Founder ratification."""
    engine = get_engine()
    changed = engine.complete_beacon()
    if changed:
        console.print("[bold green]✔ Active Cognitive Beacon marked as COMPLETED.[/bold green]")
    else:
        console.print("[yellow]No active beacon was found to complete.[/yellow]")


if __name__ == "__main__":
    app()
