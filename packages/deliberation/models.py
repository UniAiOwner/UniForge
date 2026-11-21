"""
Domain Models for the UniCortex Frontal Lobe & Deliberative Council Engine.
Governs System 2 MCTS tree search and multi-council deliberation.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CouncilRole(str, Enum):
    ARCHITECTURE_AND_DOMAIN = "ARCHITECTURE_AND_DOMAIN"
    SURFACES_AND_INTERACTION = "SURFACES_AND_INTERACTION"
    DATA_AND_HARDWARE = "DATA_AND_HARDWARE"
    SECURITY_AND_APPSEC = "SECURITY_AND_APPSEC"
    DEVILS_ADVOCATE_AND_RISK = "DEVILS_ADVOCATE_AND_RISK"


class MCTSAction(BaseModel):
    action_id: str = Field(description="Unique action identifier")
    description: str = Field(description="Action description or strategy")
    code_patch: Optional[str] = Field(default=None, description="Proposed code snippet or patch")
    expected_outcome: str = Field(description="Anticipated technical outcome")


class TrajectoryStep(BaseModel):
    step_index: int = Field(description="Step index in trajectory")
    action: MCTSAction = Field(description="Action executed at this step")
    score: float = Field(default=0.0, description="Step quality score (0.0 to 1.0)")
    sandbox_verified: bool = Field(default=False, description="Whether executed inside UniExec sandbox")
    execution_time_ms: float = Field(default=0.0)


class TrajectoryPlan(BaseModel):
    plan_id: str = Field(description="Unique plan identifier")
    goal: str = Field(description="Goal or problem being solved")
    steps: List[TrajectoryStep] = Field(default_factory=list)
    overall_value: float = Field(default=0.0, description="Cumulative trajectory evaluation score")
    is_sound: bool = Field(default=False, description="Whether trajectory satisfies all invariants")


class CouncilVote(BaseModel):
    council_role: CouncilRole = Field(description="Council casting the vote")
    consensus_score: float = Field(description="Consensus score (0.0 to 1.0)")
    is_ratified: bool = Field(description="Whether council ratifies the proposal")
    critiques: List[str] = Field(default_factory=list, description="Constructive critiques or concerns")
    actionable_directives: List[str] = Field(default_factory=list, description="Mandatory directives")
    hard_constraints_enforced: List[str] = Field(default_factory=list, description="Constitutional constraints enforced")
    latency_ms: float = Field(default=0.0)


class PlenaryDecision(BaseModel):
    proposal_topic: str = Field(description="Topic or proposal deliberated")
    overall_consensus_score: float = Field(description="Average consensus across all 5 councils")
    is_ratified: bool = Field(description="Whether proposal passed plenary consensus (>= 4/5 votes)")
    council_votes: Dict[str, CouncilVote] = Field(default_factory=dict)
    final_directives: List[str] = Field(default_factory=list)
    artifact_soundness_score: float = Field(default=1.0, description="Soundness score from UniVerify")
    z3_formally_verified: bool = Field(default=True, description="Whether Z3 proved mathematical invariants")
    deliberation_duration_ms: float = Field(default=0.0)
