"""
Unit Test Suite for UniCortex Frontal Lobe & Deliberation Engine.
Verifies MCTS tree planning, individual council invariants, and plenary consensus.
"""

import sys
import textwrap
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deliberation.models import CouncilRole
from deliberation.mcts_planner import MCTSPlanner
from deliberation.sovereign_councils import SovereignCouncilsEngine
from deliberation.frontal_lobe import UniCortexFrontalLobe


def test_mcts_planner_expansion_and_trajectory():
    """Verify MCTS planner searches tree and synthesizes a valid trajectory."""
    planner = MCTSPlanner(max_depth=3, num_simulations=6)
    plan = planner.plan_trajectory(goal="Refactor authentication to Argon2id with RTR")
    assert len(plan.steps) > 0
    assert plan.overall_value > 0.0
    assert plan.plan_id.startswith("plan-")


def test_council_data_and_hardware_law_acc_001():
    """Verify Data & Hardware Council rejects Float/Double money in invoices."""
    engine = SovereignCouncilsEngine()
    bad_code = """
    class InvoiceCalculator {
        val totalAmount: Double = 100.50
    }
    """
    vote = engine.evaluate_data_and_hardware("Invoice Accounting", bad_code)
    assert vote.is_ratified is False
    assert any("Integer Paise" in c for c in vote.critiques)


def test_council_security_law_000_suppress():
    """Verify Security & AppSec Council rejects @Suppress under Law-000."""
    engine = SovereignCouncilsEngine()
    bad_code = """
    @Suppress("UNCHECKED_CAST")
    fun castObject(obj: Any): String = obj as String
    """
    vote = engine.evaluate_security_and_appsec("Type Casting", bad_code)
    assert vote.is_ratified is False
    assert any("@Suppress" in c for c in vote.critiques)


def test_council_surfaces_sub_48dp_touch():
    """Verify Surfaces & Interaction Council flags touch targets smaller than 48dp."""
    engine = SovereignCouncilsEngine()
    bad_code = """
    IconButton(
        modifier = Modifier.size(32.dp),
        onClick = {}
    )
    """
    vote = engine.evaluate_surfaces_and_interaction("Cart Button", bad_code)
    assert any("48dp" in c for c in vote.critiques)


def test_council_devils_advocate_parsimony():
    """Verify Devil's Advocate flags excessive manager/factory boilerplate."""
    engine = SovereignCouncilsEngine()
    overengineered = """
    class AbstractUserManagerFactoryManager {
        fun createManagerFactory(): UserManagerFactory = UserManagerFactory()
    }
    """
    vote = engine.evaluate_devils_advocate_and_risk("User Auth", overengineered)
    assert any("Parsimony" in d for d in vote.actionable_directives)


def test_frontal_lobe_plenary_clean_proposal_ratified():
    """Verify clean compliant proposal passes plenary deliberation and receives RATIFIED verdict."""
    lobe = UniCortexFrontalLobe()
    clean_proposal = textwrap.dedent("""
    from pydantic import BaseModel, Field

    class TransactionRecord(BaseModel):
        transaction_id: str = Field(description="Unique UUID")
        account_id: str = Field(description="Account identifier")
        amount_paise: int = Field(ge=0, description="Integer paise amount")
        is_credit: bool = Field(description="Credit or debit indicator")

    def process_transaction(current_balance_paise: int, tx: TransactionRecord) -> int:
        assert current_balance_paise >= 0, "Account balance must be non-negative"
        if tx.is_credit:
            return current_balance_paise + tx.amount_paise
        else:
            if tx.amount_paise > current_balance_paise:
                raise ValueError("Insufficient funds for debit")
            return current_balance_paise - tx.amount_paise
    """)
    decision = lobe.deliberate(topic="Clean Ledger Transaction Engine", spec_or_code=clean_proposal)
    assert decision.is_ratified is True
    assert decision.overall_consensus_score >= 0.75
    assert decision.artifact_soundness_score >= 0.75
    assert len(decision.council_votes) == 5
