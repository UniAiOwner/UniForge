"""
UniMemory Engine Facade
=======================
Primary high-level API for the UniMemory Substrate.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from unimemory.db import get_db_connection, init_db
from unimemory.working import WorkingMemoryManager
from unimemory.episodic import EpisodicMemoryManager
from unimemory.semantic import SemanticGraphManager
from unimemory.codebase_vfs import CodebaseVFSManager
from unimemory.retriever import UnifiedRetriever
from unimemory.beacon import BeaconManager
from unimemory.models import MemoryRecallResult, CognitiveBeacon, BeaconDriftCheckResult
from unimemory.config import BRAIN_MEMORY_DB


class UniMemoryEngine:

    def __init__(self, db_path: Optional[Path] = None, read_only: bool = False):
        self.db_path = db_path or BRAIN_MEMORY_DB
        if read_only:
            self.conn = get_db_connection(self.db_path, read_only=True)
        else:
            try:
                self.conn = init_db(self.db_path)
            except (sqlite3.OperationalError, OSError):
                self.conn = get_db_connection(self.db_path, read_only=True)
        self.working = WorkingMemoryManager(self.conn)
        self.episodic = EpisodicMemoryManager(self.conn)
        self.semantic = SemanticGraphManager(self.conn)
        self.vfs = CodebaseVFSManager(self.conn)
        self.retriever = UnifiedRetriever(self.conn)
        self.beacon = BeaconManager(db_conn=self.conn, db_path=self.db_path)

    def recall(
        self,
        query: str,
        project_scope: Optional[str] = None,
        top_k: int = 5
    ) -> MemoryRecallResult:
        """Sub-15ms multi-tier hybrid recall."""
        return self.retriever.recall(query=query, project_scope=project_scope, top_k=top_k)

    def store_fact(
        self,
        subject: str,
        predicate: str,
        target_object: str,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """Stores a bi-temporal semantic fact with automated edge evolution."""
        fact = self.semantic.add_fact(subject, predicate, target_object, confidence)
        return fact.model_dump()

    def record_episode(
        self,
        project: str,
        goal: str,
        steps_taken: List[str],
        errors_encountered: List[str],
        root_cause_lesson: str,
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        """Stores an episodic execution trace for Law-STARK failure blocking."""
        ep = self.episodic.record_episode(
            project=project,
            goal=goal,
            steps_taken=steps_taken,
            errors_encountered=errors_encountered,
            root_cause_lesson=root_cause_lesson,
            status=status
        )
        return ep.model_dump()

    def set_working(
        self,
        key: str,
        value: Any,
        project_scope: str = "GLOBAL",
        priority: int = 1
    ) -> Dict[str, Any]:
        """Sets working memory context."""
        item = self.working.set(key, value, project_scope, priority)
        return item.model_dump()

    def sync_project(self, project_path: Path, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Indexes source code symbols and AST elements for a project."""
        p_path = Path(project_path)
        p_name = project_name or p_path.name
        return self.vfs.index_project(project_name=p_name, project_path=p_path)

    def set_beacon(
        self,
        mission_name: str,
        parent_goal: str,
        active_milestone: str,
        in_scope_paths: List[str],
        forbidden_domains: List[str]
    ) -> CognitiveBeacon:
        """Sets and activates a new Cognitive Beacon anchor."""
        return self.beacon.set_active_beacon(
            mission_name=mission_name,
            parent_goal=parent_goal,
            active_milestone=active_milestone,
            in_scope_paths=in_scope_paths,
            forbidden_domains=forbidden_domains
        )

    def get_beacon(self) -> Optional[CognitiveBeacon]:
        """Gets currently active Cognitive Beacon."""
        return self.beacon.get_active_beacon()

    def check_drift(self, target_path: Optional[str] = None, intent_summary: str = "") -> BeaconDriftCheckResult:
        """Verifies if an action or file path deviates from the active beacon mission."""
        return self.beacon.check_drift(target_path=target_path, intent_summary=intent_summary)

    def beacon_header(self) -> str:
        """Returns compact < 35 token ambient beacon header."""
        return self.beacon.format_beacon_header()

    def complete_beacon(self) -> bool:
        """Completes active beacon."""
        return self.beacon.complete_beacon()

    def doctor(self) -> Dict[str, Any]:
        """Runs health checks, integrity verification, and counts records across all tiers."""
        cur = self.conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        integrity = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM working_context;")
        working_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM episodic_ledger;")
        episodic_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM semantic_triplets WHERE is_current = 1;")
        active_facts_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM codebase_symbols_vfs;")
        symbols_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM memory_fts;")
        fts_count = cur.fetchone()[0]

        active_beacon = self.get_beacon()

        return {
            "database_path": str(self.db_path),
            "integrity_check": integrity,
            "is_healthy": (integrity == "ok"),
            "working_context_count": working_count,
            "episodic_records_count": episodic_count,
            "active_semantic_facts_count": active_facts_count,
            "indexed_symbols_count": symbols_count,
            "fts5_indexed_documents": fts_count,
            "active_beacon": active_beacon.to_ambient_header() if active_beacon else "NONE"
        }


# Singleton Accessor
_ENGINE_INSTANCE: Optional[UniMemoryEngine] = None

def get_engine() -> UniMemoryEngine:
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = UniMemoryEngine()
    return _ENGINE_INSTANCE
