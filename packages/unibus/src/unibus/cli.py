"""
UniBus Typer Command Line Interface.
"""

import sys
import json
import asyncio
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from unibus import __version__
from unibus.bus import UniBus
from unibus.models import EventPriority, DecisionStatus, AgentStatus
from unibus.uds import UDSServer

app = typer.Typer(
    name="unibus",
    help="UniBus: Sovereign Real-Time Unix Domain Socket IPC & Shared Bus State Subsystem",
    no_args_is_help=True
)

constraint_app = typer.Typer(name="constraint", help="Manage Architectural Constraints Tuple Space")
decision_app = typer.Typer(name="decision", help="Manage Architectural Decision Records (ADRs)")
lease_app = typer.Typer(name="lease", help="Manage Distributed Work Mutex Leases")
event_app = typer.Typer(name="event", help="Manage Priority Event Pub/Sub")
agent_app = typer.Typer(name="agent", help="Manage Agent Heartbeats & Liveness")
daemon_app = typer.Typer(name="daemon", help="Manage Unix Domain Socket Daemon")

app.add_typer(constraint_app)
app.add_typer(decision_app)
app.add_typer(lease_app)
app.add_typer(event_app)
app.add_typer(agent_app)
app.add_typer(daemon_app)

console = Console()
bus = UniBus()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context, version: bool = typer.Option(False, "--version", "-v", help="Show version")):
    if version:
        console.print(f"[bold cyan]UniBus[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.command(name="doctor")
def doctor():
    """Diagnose health of SQLite WAL bus and Unix Domain Socket daemon."""
    report = bus.doctor()
    table = Table(title="UniBus Diagnostic Report", show_header=True, header_style="bold magenta")
    table.add_column("Subsystem", style="dim")
    table.add_column("Status / Metric", justify="left")

    overall_color = "green" if report["status"] == "HEALTHY" else "yellow"
    table.add_row("Overall Health", f"[{overall_color}]{report['status']}[/{overall_color}]")
    table.add_row("Bus DB", f"{report['db_path']} ({'EXISTS & WRITABLE' if report['db_writable'] else 'UNWRITABLE'})")
    socket_color = "green" if report["socket_daemon_active"] else "yellow"
    table.add_row("UDS Socket Daemon", f"[{socket_color}]{'ACTIVE' if report['socket_daemon_active'] else 'INACTIVE (Fallback to direct WAL)'}[/{socket_color}] ({report['socket_path']})")
    table.add_row("Active Constraints", str(report["constraints_count"]))
    table.add_row("Architectural Decisions", str(report["decisions_count"]))
    table.add_row("Active Work Leases", str(report["active_leases"]))
    table.add_row("Pending Events", str(report["pending_events_count"]))

    console.print(table)


@app.command(name="status")
def status():
    """Show current bus metrics overview."""
    st = bus.status()
    console.print(Panel(
        f"[bold]Active Constraints:[/bold] {st['constraints']}\n"
        f"[bold]Recorded Decisions (ADRs):[/bold] {st['decisions']}\n"
        f"[bold]Active Work Leases:[/bold] {st['active_leases']}\n"
        f"[bold]Pending Priority Events:[/bold] {st['pending_events']}\n"
        f"[bold]Active Agent Heartbeats:[/bold] {st['active_agents']}\n"
        f"[bold]UDS Socket Active:[/bold] {'Yes' if st['socket_active'] else 'No (Direct WAL Mode)'}",
        title="UniBus System State",
        border_style="cyan"
    ))


# ==========================================
# 1. Constraint Commands
# ==========================================

@constraint_app.command(name="set")
def constraint_set(
    key: str = typer.Argument(..., help="Constraint key name"),
    value: str = typer.Argument(..., help="Constraint value (JSON or string)"),
    domain: str = typer.Option("GENERAL", "--domain", "-d", help="Domain: SECURITY, DATABASE, UI, etc."),
    unit: Optional[str] = typer.Option(None, "--unit", "-u", help="Measurement unit"),
    rationale: Optional[str] = typer.Option(None, "--rationale", "-r", help="Why this constraint exists"),
    agent: str = typer.Option("system", "--agent", "-a", help="Agent imposing this constraint")
):
    """Set or update an architectural constraint."""
    try:
        parsed_val = json.loads(value)
    except Exception:
        parsed_val = value

    record = bus.set_constraint(
        key=key,
        value=parsed_val,
        domain=domain,
        unit=unit,
        rationale=rationale,
        imposing_agent=agent
    )
    console.print(f"[bold green]✔ Constraint Set:[/bold green] [bold cyan]{record.constraint_key}[/bold cyan] = {record.value_json} (v{record.version}, domain={record.domain})")


@constraint_app.command(name="get")
def constraint_get(
    key: str = typer.Argument(..., help="Constraint key name"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter domain")
):
    """Query a specific architectural constraint."""
    rec = bus.get_constraint(key=key, domain=domain)
    if not rec:
        console.print(f"[bold red]✘ Constraint '{key}' not found.[/bold red]")
        raise typer.Exit(code=1)
    console.print(f"[bold cyan]{rec.constraint_key}[/bold cyan]: {rec.value_json} [dim]({rec.unit or 'no unit'})[/dim]")
    if rec.rationale:
        console.print(f"  [italic dim]Rationale: {rec.rationale}[/italic dim]")
    console.print(f"  [dim]Domain: {rec.domain} | Version: {rec.version} | By: {rec.imposing_agent}[/dim]")


@constraint_app.command(name="list")
def constraint_list(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter domain")
):
    """List all architectural constraints."""
    items = bus.list_constraints(domain=domain)
    if not items:
        console.print("[dim]No constraints recorded.[/dim]")
        return

    table = Table(title="Architectural Constraints", show_header=True, header_style="bold blue")
    table.add_column("Domain", style="cyan")
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_column("Unit", style="dim")
    table.add_column("Ver", justify="right")
    table.add_column("Imposing Agent", style="dim")

    for c in items:
        table.add_row(c.domain, c.constraint_key, str(c.value_json), c.unit or "-", str(c.version), c.imposing_agent)
    console.print(table)


# ==========================================
# 2. Decision Commands (ADR)
# ==========================================

@decision_app.command(name="log")
def decision_log(
    title: str = typer.Argument(..., help="Decision title"),
    decision_text: str = typer.Option("", "--text", "-t", help="Architectural choice details"),
    rationale: str = typer.Option("", "--rationale", "-r", help="Why this choice was made"),
    consequences: str = typer.Option("", "--consequences", "-c", help="Trade-offs & downstream impact"),
    author: str = typer.Option("system", "--author", "-a", help="Authoring agent name"),
    status: DecisionStatus = typer.Option(DecisionStatus.ACCEPTED, "--status", "-s", help="ACCEPTED/SUPERSEDED/REVOKED")
):
    """Log an Architectural Decision Record (ADR)."""
    dec = bus.log_decision(
        title=title,
        decision_text=decision_text,
        rationale=rationale,
        consequences=consequences,
        author_agent=author,
        status=status
    )
    console.print(f"[bold green]✔ ADR Recorded:[/bold green] [{dec.decision_id}] {dec.title} ({dec.status.value})")


@decision_app.command(name="list")
def decision_list(
    status: Optional[DecisionStatus] = typer.Option(None, "--status", "-s", help="Filter by status")
):
    """List recorded architectural decisions."""
    decisions = bus.list_decisions(status=status)
    if not decisions:
        console.print("[dim]No decisions recorded.[/dim]")
        return

    table = Table(title="Architectural Decision Records (ADRs)", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Author", style="dim")
    table.add_column("Timestamp", style="dim")

    for d in decisions:
        status_color = "green" if d.status == DecisionStatus.ACCEPTED else ("yellow" if d.status == DecisionStatus.SUPERSEDED else "red")
        table.add_row(
            d.decision_id,
            d.title,
            f"[{status_color}]{d.status.value}[/{status_color}]",
            d.author_agent,
            d.timestamp[:19]
        )
    console.print(table)


# ==========================================
# 3. Work Lease Commands
# ==========================================

@lease_app.command(name="acquire")
def lease_acquire(
    resource_id: str = typer.Argument(..., help="Resource identifier (file path, module, task ID)"),
    owner: str = typer.Option("system", "--owner", "-o", help="Agent acquiring the lease"),
    ttl: int = typer.Option(60, "--ttl", "-t", help="Lease duration in seconds")
):
    """Acquire an atomic mutex lease on a resource."""
    ok, lease, reason = bus.acquire_lease(
        resource_id=resource_id,
        owner_agent=owner,
        ttl_seconds=ttl
    )
    if not ok:
        console.print(f"[bold red]✘ Lock Contention Failed:[/bold red] {reason}")
        raise typer.Exit(code=1)
    console.print(f"[bold green]✔ Lease Acquired:[/bold green] [bold cyan]{resource_id}[/bold cyan] locked by '{owner}' for {ttl}s (expires {lease.expires_at[:19]})")


@lease_app.command(name="release")
def lease_release(
    resource_id: str = typer.Argument(..., help="Resource identifier"),
    owner: Optional[str] = typer.Option(None, "--owner", "-o", help="Verify owner matches")
):
    """Release an active work lease."""
    released = bus.release_lease(resource_id=resource_id, owner_agent=owner)
    if released:
        console.print(f"[bold green]✔ Lease Released:[/bold green] {resource_id}")
    else:
        console.print(f"[bold yellow]⚠ No active lease found to release for {resource_id}[/bold yellow]")


@lease_app.command(name="list")
def lease_list(
    all_leases: bool = typer.Option(False, "--all", "-a", help="Include expired leases")
):
    """List active work leases."""
    leases = bus.list_leases(active_only=not all_leases)
    if not leases:
        console.print("[dim]No active work leases held.[/dim]")
        return

    table = Table(title="Work Item Leases", show_header=True, header_style="bold green")
    table.add_column("Resource", style="bold cyan")
    table.add_column("Owner", style="bold")
    table.add_column("Expires At", style="dim")
    table.add_column("Status")

    for l in leases:
        status_str = "[red]EXPIRED[/red]" if l.is_expired() else "[green]ACTIVE[/green]"
        table.add_row(l.resource_id, l.owner_agent, l.expires_at[:19], status_str)
    console.print(table)


# ==========================================
# 4. Priority Event Commands
# ==========================================

@event_app.command(name="publish")
def event_publish(
    topic: str = typer.Argument(..., help="Event topic name"),
    payload: str = typer.Argument("{}", help="JSON payload string"),
    priority: EventPriority = typer.Option(EventPriority.NORMAL, "--priority", "-p", help="CRITICAL/HIGH/NORMAL/LOW")
):
    """Publish a priority event onto the Bus and UDS socket."""
    try:
        parsed_payload = json.loads(payload)
    except Exception:
        parsed_payload = {"raw": payload}

    rec = bus.publish_event(topic=topic, payload=parsed_payload, priority=priority)
    color = "red" if priority == EventPriority.CRITICAL else ("yellow" if priority == EventPriority.HIGH else "green")
    console.print(f"[bold {color}]✔ Event Published:[/bold {color}] [{rec.event_id}] {rec.topic} ({rec.priority.value})")


@event_app.command(name="poll")
def event_poll(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Topic pattern or filter"),
    priority: Optional[EventPriority] = typer.Option(None, "--priority", "-p", help="Filter priority"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max events to return")
):
    """Poll pending events ordered by priority."""
    events = bus.poll_events(topic=topic, priority=priority, limit=limit)
    if not events:
        console.print("[dim]No pending events found.[/dim]")
        return

    table = Table(title="Pending Bus Events", show_header=True, header_style="bold yellow")
    table.add_column("ID", style="cyan")
    table.add_column("Priority", style="bold")
    table.add_column("Topic")
    table.add_column("Payload Preview", style="dim")
    table.add_column("Created At", style="dim")

    for e in events:
        p_color = "red" if e.priority == EventPriority.CRITICAL else ("yellow" if e.priority == EventPriority.HIGH else "green")
        preview = e.payload_json[:40] + ("..." if len(e.payload_json) > 40 else "")
        table.add_row(
            e.event_id,
            f"[{p_color}]{e.priority.value}[/{p_color}]",
            e.topic,
            preview,
            e.created_at[:19]
        )
    console.print(table)


@event_app.command(name="claim")
def event_claim(
    event_id: str = typer.Argument(..., help="Event ID"),
    agent: str = typer.Option("system", "--agent", "-a", help="Agent claiming processing")
):
    """Claim a pending event."""
    claimed = bus.claim_event(event_id=event_id, agent_name=agent)
    if claimed:
        console.print(f"[bold green]✔ Event Claimed:[/bold green] [{event_id}] by '{agent}'")
    else:
        console.print(f"[bold red]✘ Failed to claim event [{event_id}] (already claimed or not found)[/bold red]")
        raise typer.Exit(code=1)


@event_app.command(name="resolve")
def event_resolve(
    event_id: str = typer.Argument(..., help="Event ID")
):
    """Mark an event as resolved."""
    resolved = bus.resolve_event(event_id=event_id)
    if resolved:
        console.print(f"[bold green]✔ Event Resolved:[/bold green] [{event_id}]")
    else:
        console.print(f"[bold yellow]⚠ Event [{event_id}] not found or already resolved[/bold yellow]")


# ==========================================
# 5. Agent Heartbeat Commands
# ==========================================

@agent_app.command(name="heartbeat")
def agent_heartbeat(
    agent_name: str = typer.Argument(..., help="Agent name or prime"),
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Current task being performed")
):
    """Send agent heartbeat ping."""
    rec = bus.record_heartbeat(agent_name=agent_name, current_task=task)
    console.print(f"[bold green]✔ Heartbeat Recorded:[/bold green] {rec.agent_name} ({rec.status.value}) [dim]task: {rec.current_task or 'none'}[/dim]")


@agent_app.command(name="list")
def agent_list(
    all_agents: bool = typer.Option(False, "--all", "-a", help="Include stale agents")
):
    """List registered agent heartbeats."""
    agents = bus.list_agents(active_only=not all_agents)
    if not agents:
        console.print("[dim]No agent heartbeats recorded.[/dim]")
        return

    table = Table(title="Agent Roster & Liveness", show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="bold")
    table.add_column("Status")
    table.add_column("Current Task", style="dim")
    table.add_column("Last Seen", style="dim")

    for a in agents:
        st_color = "green" if a.status == AgentStatus.ACTIVE and not a.is_stale() else "red"
        table.add_row(
            a.agent_name,
            f"[{st_color}]{a.status.value}[/{st_color}]",
            a.current_task or "-",
            a.last_seen[:19]
        )
    console.print(table)


# ==========================================
# 6. Daemon Commands
# ==========================================

@daemon_app.command(name="run")
def daemon_run():
    """Run the Unix Domain Socket broadcast daemon in foreground."""
    server = UDSServer(bus.socket_path)
    console.print(f"[bold green]Starting UniBus UDS Daemon on {server.socket_path}...[/bold green]")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(server.start())
        console.print("[bold cyan]UniBus UDS Daemon listening. Press Ctrl+C to stop.[/bold cyan]")
        loop.run_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping UniBus UDS Daemon...[/yellow]")
        loop.run_until_complete(server.stop())
        console.print("[bold green]Stopped cleanly.[/bold green]")


def main():
    app()


if __name__ == "__main__":
    main()
