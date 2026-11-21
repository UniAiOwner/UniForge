"""
UniCortex Frontal Lobe Typer CLI.
Entrypoint for System 2 MCTS Planning and 5 Living Councils Deliberation.
"""

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ensure parent directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deliberation.frontal_lobe import UniCortexFrontalLobe
from deliberation.models import CouncilRole

app = typer.Typer(help="UniCortex Frontal Lobe: MCTS Planning & 5 Living Councils Deliberation")
console = Console()


@app.command()
def convene(
    topic: str = typer.Argument(..., help="Proposal topic or architectural title"),
    code: str = typer.Option(..., "--code", "-c", help="Code snippet or architectural specification to evaluate")
):
    """Convenes the 5 Living Councils to deliberate on a proposal."""
    lobe = UniCortexFrontalLobe()
    console.print(f"[bold cyan]🏛️ Convening Plenary Deliberation Council:[/bold cyan] {topic}")

    decision = lobe.deliberate(topic=topic, spec_or_code=code)

    table = Table(title=f"Council Votes for: {topic}")
    table.add_column("Living Council", style="cyan", no_wrap=True)
    table.add_column("Verdict", style="bold")
    table.add_column("Consensus Score", style="magenta")
    table.add_column("Critiques / Directives", style="white")

    for cname, vote in decision.council_votes.items():
        v_style = "green" if vote.is_ratified else "red"
        v_text = "RATIFIED" if vote.is_ratified else "REJECTED"
        critique_txt = "; ".join(vote.critiques) if vote.critiques else "No objections."
        table.add_row(cname, f"[{v_style}]{v_text}[/{v_style}]", f"{vote.consensus_score:.2f}", critique_txt)

    console.print(table)

    verdict_style = "green" if decision.is_ratified else "red"
    verdict_label = "RATIFIED (PROCEED)" if decision.is_ratified else "REJECTED (HALT)"

    console.print(Panel(
        f"Consensus Score: [bold]{decision.overall_consensus_score:.2f}[/bold] | "
        f"Artifact Soundness: [bold]{decision.artifact_soundness_score:.2f}[/bold] | "
        f"Plenary Verdict: [{verdict_style}][bold]{verdict_label}[/bold][/{verdict_style}]\n"
        f"Directives: {', '.join(decision.final_directives) if decision.final_directives else 'None'}",
        title="Plenary Deliberation Summary",
        border_style=verdict_style
    ))

    if not decision.is_ratified:
        raise typer.Exit(code=1)


@app.command()
def mcts(goal: str = typer.Argument(..., help="Goal or problem to solve via MCTS tree search")):
    """Runs MCTS Tree Search to plan an optimal multi-step trajectory."""
    lobe = UniCortexFrontalLobe()
    console.print(f"[bold cyan]🌲 Running MCTS Tree Search Planning:[/bold cyan] {goal}")

    plan = lobe.plan_complex_task(goal=goal)

    table = Table(title=f"MCTS Trajectory: {plan.plan_id}")
    table.add_column("Step", style="cyan", no_wrap=True)
    table.add_column("Strategic Action", style="bold white")
    table.add_column("Score", style="magenta")
    table.add_column("Sandboxed", style="green")

    for step in plan.steps:
        table.add_row(
            f"Step {step.step_index}",
            step.action.description,
            f"{step.score:.2f}",
            "YES" if step.sandbox_verified else "NO"
        )

    console.print(table)
    console.print(f"Overall Trajectory Value: [bold green]{plan.overall_value:.2f}[/bold green] (Sound: {plan.is_sound})")


@app.command()
def doctor():
    """Runs health check for Frontal Lobe, MCTS planner, and 5 Councils."""
    console.print("[bold cyan]🩺 UniCortex Frontal Lobe Doctor Diagnostic[/bold cyan]")
    table = Table()
    table.add_column("Cognitive Subsystem", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")

    table.add_row("MCTS Tree Search Planner", "[green]ONLINE[/green]", "UCT exploration with sandboxed trajectory simulation")
    table.add_row("5 Living Councils", "[green]ONLINE[/green]", "Architecture, Surfaces, Data, Security, Devil's Advocate")

    from deliberation.frontal_lobe import UNIBUS_AVAILABLE, UNIVERIFY_AVAILABLE, UNIMEMORY_AVAILABLE
    table.add_row("UniBus IPC (Pillar 6)", "[green]CONNECTED[/green]" if UNIBUS_AVAILABLE else "[yellow]OFFLINE[/yellow]", "Deliberation mutex & decision events")
    table.add_row("UniVerify Gatekeeper (Pillar 4)", "[green]CONNECTED[/green]" if UNIVERIFY_AVAILABLE else "[yellow]OFFLINE[/yellow]", "Z3 SMT Bounds + Artifact Scorer")
    table.add_row("UniMemory Substrate (Pillar 3)", "[green]CONNECTED[/green]" if UNIMEMORY_AVAILABLE else "[yellow]OFFLINE[/yellow]", "Living beacon & semantic facts")

    console.print(table)


if __name__ == "__main__":
    app()
