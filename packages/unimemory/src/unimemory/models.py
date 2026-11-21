"""
UniMemory Data Models
=====================
Strict Pydantic models for all 5 cognitive memory tiers.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time
from datetime import datetime, timezone


class WorkingMemoryItem(BaseModel):
    key: str
    value_json: str
    project_scope: str = "GLOBAL"
    priority: int = 1  # 1 = Normal, 2 = High, 3 = Critical
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None


class EpisodicEntry(BaseModel):
    episode_id: str
    project: str
    goal: str
    steps_taken: List[str] = Field(default_factory=list)
    errors_encountered: List[str] = Field(default_factory=list)
    root_cause_lesson: str = ""
    status: str = "SUCCESS"  # SUCCESS, FAILED, PARTIAL
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SemanticFact(BaseModel):
    fact_id: str
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    valid_from: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_to: Optional[str] = None
    is_current: bool = True


class SymbolItem(BaseModel):
    project: str
    symbol_name: str
    symbol_type: str  # class, function, interface, composable, entity
    file_path: str
    line_number: int
    doc_summary: str = ""
    symbol_hash: str = ""


class CognitiveBeacon(BaseModel):
    id: str
    mission_name: str
    parent_goal: str
    active_milestone: str
    in_scope_paths: List[str] = Field(default_factory=list)
    forbidden_domains: List[str] = Field(default_factory=list)
    status: str = "ACTIVE"  # ACTIVE, COMPLETED, REVOKED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_ambient_header(self) -> str:
        """Compact < 35 token ambient header for turn injection."""
        return f"⬢ [BEACON: {self.mission_name} | ACTIVE: {self.active_milestone} | LOCKED]"


class BeaconDriftCheckResult(BaseModel):
    allowed: bool
    beacon_id: Optional[str] = None
    violation_reason: Optional[str] = None


class MemoryRecallResult(BaseModel):
    query: str
    working_context: List[WorkingMemoryItem] = Field(default_factory=list)
    episodic_lessons: List[EpisodicEntry] = Field(default_factory=list)
    semantic_facts: List[SemanticFact] = Field(default_factory=list)
    codebase_symbols: List[SymbolItem] = Field(default_factory=list)
    retrieval_latency_ms: float = 0.0

    def to_readable_summary(self) -> str:
        parts = [f"=== MEMORY RECALL FOR: '{self.query}' (Latency: {self.retrieval_latency_ms:.2f}ms) ==="]
        if self.working_context:
            parts.append("\n📌 [WORKING CONTEXT]")
            for w in self.working_context:
                parts.append(f"  • {w.key}: {w.value_json}")
        if self.episodic_lessons:
            parts.append("\n📜 [EPISODIC LESSONS / LAW-STARK]")
            for ep in self.episodic_lessons:
                parts.append(f"  • [{ep.status}] {ep.project}: {ep.goal} -> Lesson: {ep.root_cause_lesson}")
        if self.semantic_facts:
            parts.append("\n🕸️ [SEMANTIC KNOWLEDGE GRAPH]")
            for f in self.semantic_facts:
                parts.append(f"  • {f.subject} --[{f.predicate}]--> {f.object} (conf: {f.confidence})")
        if self.codebase_symbols:
            parts.append("\n💻 [CODEBASE SYMBOLS]")
            for s in self.codebase_symbols[:5]:
                parts.append(f"  • [{s.symbol_type.upper()}] {s.symbol_name} in {s.file_path}:{s.line_number}")
        return "\n".join(parts)
