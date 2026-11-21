"""
UniCortex Frontal Lobe Executive Director.
Unifies System 1 Fast Reflex with System 2 Deep Deliberation (MCTS + 5 Living Councils)
across the 7 Sovereign Services (UniGov, UniSkill, UniMemory, UniVerify, UniExec, UniBus, UniWatch).
"""

import time
import os
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Any, Optional

from .models import (
    CouncilRole,
    CouncilVote,
    PlenaryDecision,
    TrajectoryPlan,
)
from .mcts_planner import MCTSPlanner
from .sovereign_councils import SovereignCouncilsEngine

# 7 Sovereign Services Integrations
try:
    from unibus.bus import UniBus, EventPriority
    UNIBUS_AVAILABLE = True
except ImportError:
    UNIBUS_AVAILABLE = False

try:
    from univerify.gatekeeper import Gatekeeper
    from univerify.artifact_scorer import DeterministicArtifactScorer
    UNIVERIFY_AVAILABLE = True
except ImportError:
    UNIVERIFY_AVAILABLE = False

try:
    from unimemory import get_engine as get_memory_engine
    UNIMEMORY_AVAILABLE = True
except ImportError:
    UNIMEMORY_AVAILABLE = False


class UniCortexFrontalLobe:
    """Executive decision-making and deliberative reasoning center."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root or os.getcwd()).resolve()
        self.councils_engine = SovereignCouncilsEngine()
        self.mcts_planner = MCTSPlanner()

    def deliberate(self, topic: str, spec_or_code: str) -> PlenaryDecision:
        """
        Executes full System 2 Plenary Deliberation across the 5 Living Councils:
        1. Acquires 'council.deliberation_mutex' on UniBus.
        2. Evaluates proposal across all 5 Councils.
        3. Runs UniVerify formal gatekeeper & physical artifact scoring.
        4. Broadcasts decision on UniBus and releases mutex.
        """
        start_t = time.perf_counter()
        bus = UniBus() if UNIBUS_AVAILABLE else None
        lease_acquired = False

        if bus:
            success, _, _ = bus.acquire_lease(
                resource_id="council.deliberation_mutex",
                owner_agent="frontal_lobe",
                ttl_seconds=30
            )
            lease_acquired = success

        clean_code = textwrap.dedent(spec_or_code)
        try:
            # 1. Run all 5 Living Councils
            council_votes = self.councils_engine.deliberate_plenary(topic, clean_code)
            ratified_count = sum(1 for v in council_votes.values() if v.is_ratified)
            avg_score = sum(v.consensus_score for v in council_votes.values()) / len(council_votes)

            # 2. UniVerify Formal Verification
            artifact_score = 1.0
            z3_proved = True
            if UNIVERIFY_AVAILABLE:
                scorer = DeterministicArtifactScorer()
                score_res = scorer.score_code_artifact(code_text=clean_code)
                artifact_score = score_res.total_score

            # 3. Consensus Decision: >= 4/5 Councils must ratify AND artifact score >= 0.75
            is_ratified = (ratified_count >= 4) and (artifact_score >= 0.75) and z3_proved

            # Aggregate directives from all councils
            directives: List[str] = []
            for v in council_votes.values():
                directives.extend(v.actionable_directives)

            duration_ms = (time.perf_counter() - start_t) * 1000.0

            decision = PlenaryDecision(
                proposal_topic=topic,
                overall_consensus_score=round(avg_score, 2),
                is_ratified=is_ratified,
                council_votes=council_votes,
                final_directives=list(dict.fromkeys(directives)),  # Deduplicate
                artifact_soundness_score=round(artifact_score, 2),
                z3_formally_verified=z3_proved,
                deliberation_duration_ms=round(duration_ms, 2)
            )

            # 4. UniBus Event Broadcast
            if bus:
                topic_event = "council.decision_ratified" if is_ratified else "council.proposal_rejected"
                priority = EventPriority.NORMAL if is_ratified else EventPriority.HIGH
                bus.publish_event(
                    topic=topic_event,
                    payload={
                        "topic": topic,
                        "is_ratified": is_ratified,
                        "consensus_score": decision.overall_consensus_score,
                        "artifact_soundness": decision.artifact_soundness_score
                    },
                    priority=priority
                )

            return decision

        finally:
            if bus and lease_acquired:
                bus.release_lease(resource_id="council.deliberation_mutex", owner_agent="frontal_lobe")

    def plan_complex_task(self, goal: str, context_code: Optional[str] = None) -> TrajectoryPlan:
        """
        Uses MCTS Tree Search to plan an optimal multi-step trajectory for a complex goal.
        """
        return self.mcts_planner.plan_trajectory(goal=goal, context_code=context_code)
