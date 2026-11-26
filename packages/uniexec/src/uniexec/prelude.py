"""
UniExec Prelude: Pre-Bound Local Primitives
===========================================
High-performance primitives available to agents inside the sandbox without importing.
Provides sub-millisecond access to UniMemory, UniVerify, Councils, and AI Scientist.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from uniexec.config import MAX_OUTPUT_CHARS


class UniExecPrelude:
    """Namespace of local primitives exposed to sandboxed scripts."""

    @staticmethod
    def memory_recall(query: str, project_scope: Optional[str] = None, top_k: int = 5) -> str:
        """Recall facts, lessons, and AST symbols from UniMemory Substrate."""
        try:
            from unimemory.engine import get_engine
            res = get_engine().recall(query=query, project_scope=project_scope, top_k=top_k)
            return res.to_readable_summary()
        except Exception as e:
            return f"Memory recall error: {str(e)}"

    @staticmethod
    def memory_store_fact(subject: str, predicate: str, target_object: str, confidence: float = 1.0) -> Dict[str, Any]:
        """Store a bi-temporal semantic fact in UniMemory Substrate."""
        try:
            from unimemory.engine import get_engine
            return get_engine().store_fact(subject=subject, predicate=predicate, target_object=target_object, confidence=confidence)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def verify_code_gate(code_text: str, filename: str = "code.py", test_path: Optional[str] = None) -> str:
        """Run 4-tier Sovereign Code Verification Gate (Level 1 Invariants, Level 2 Z3 SMT, Level 3 Artifact Score)."""
        try:
            from univerify.gatekeeper import Gatekeeper
            res = Gatekeeper().verify_code(code_text=code_text, filename=filename, test_path=test_path)
            return res.to_readable_summary()
        except Exception as e:
            return f"Verification error: {str(e)}"

    @staticmethod
    def get_beacon() -> Dict[str, Any]:
        """Get the living active Cognitive Beacon."""
        try:
            from unimemory.engine import get_engine
            b = get_engine().get_beacon()
            if not b:
                return {"status": "NONE"}
            return b.model_dump()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def check_drift(target_path: Optional[str] = None, intent_summary: str = "") -> Dict[str, Any]:
        """Check if an action or path drifts from the active beacon mission."""
        try:
            from unimemory.engine import get_engine
            res = get_engine().check_drift(target_path=target_path, intent_summary=intent_summary)
            return res.model_dump()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def consult_scientist(inquiry: str, domain_context: Optional[str] = None) -> Dict[str, Any]:
        """Consult IQ200 AI Scientist for SOTA research literature synthesis."""
        import os
        engine_root = os.environ.get("UNICORTEX_ENGINE_DIR", str(Path.home() / ".unicortex" / "engine"))
        scientist_dir = str(Path(engine_root) / "ai_scientist")
        if scientist_dir not in sys.path:
            sys.path.insert(0, scientist_dir)
        try:
            from ai_scientist_agent import consult_scientist
            return consult_scientist(inquiry=inquiry, domain_context=domain_context)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def query_research_papers(query: str, category: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query research papers via sub-millisecond SQLite FTS5."""
        import os
        engine_root = os.environ.get("UNICORTEX_ENGINE_DIR", str(Path.home() / ".unicortex" / "engine"))
        scientist_dir = str(Path(engine_root) / "ai_scientist")
        if scientist_dir not in sys.path:
            sys.path.insert(0, scientist_dir)
        try:
            from research_index_engine import query_research_papers
            return query_research_papers(query_text=query, category=category, top_k=top_k)
        except Exception:
            return []

    @staticmethod
    def convene_council(council_name: str, proposal_topic: str, proposal_code_or_spec: str) -> Dict[str, Any]:
        """Convene one of the 5 Sovereign Councils for multi-agent deliberation."""
        import os
        engine_root = os.environ.get("UNICORTEX_ENGINE_DIR", str(Path.home() / ".unicortex" / "engine"))
        councils_dir = str(Path(engine_root) / "councils")
        if councils_dir not in sys.path:
            sys.path.insert(0, councils_dir)
        try:
            from sovereign_councils_engine import convene_council, convene_plenary
            if council_name.strip().upper() == "PLENARY":
                return convene_plenary(proposal_topic=proposal_topic, proposal_code_or_spec=proposal_code_or_spec)
            return convene_council(council_name=council_name, proposal_topic=proposal_topic, proposal_code_or_spec=proposal_code_or_spec)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def git_diff_summary(repo_path: str) -> Dict[str, Any]:
        """Gets concise git status & modified files summary without dumping megabytes."""
        p = Path(repo_path)
        if not p.exists() or not (p / ".git").exists():
            return {"error": f"Invalid git repo: {repo_path}"}
        try:
            st = subprocess.run(["git", "-C", str(p), "status", "--short"], capture_output=True, text=True, timeout=5)
            lines = [line.strip() for line in st.stdout.strip().split("\n") if line.strip()]
            return {
                "total_changed": len(lines),
                "files": lines[:10],
                "truncated": len(lines) > 10
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def bus_publish_event(topic: str, payload: Dict[str, Any], priority: str = "NORMAL") -> Dict[str, Any]:
        """Publish a real-time event to UniBus."""
        try:
            from unibus import UniBus, EventPriority
            p_enum = getattr(EventPriority, priority.upper(), EventPriority.NORMAL)
            rec = UniBus().publish_event(topic, payload, priority=p_enum)
            return rec.model_dump()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def bus_query_constraints(domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query active architectural constraints from UniBus."""
        try:
            from unibus import UniBus
            items = UniBus().list_constraints(domain=domain)
            return [c.model_dump() for c in items]
        except Exception:
            return []

    @staticmethod
    def bus_acquire_lease(resource_id: str, owner_agent: str = "code_mode", ttl_seconds: int = 60) -> Dict[str, Any]:
        """Acquire a work mutex lease on a file/module."""
        try:
            from unibus import UniBus
            ok, lease, reason = UniBus().acquire_lease(resource_id, owner_agent, ttl_seconds=ttl_seconds)
            return {
                "success": ok,
                "reason": reason,
                "lease": lease.model_dump() if lease else None
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def bus_release_lease(resource_id: str, owner_agent: Optional[str] = "code_mode") -> bool:
        """Release a work mutex lease."""
        try:
            from unibus import UniBus
            return UniBus().release_lease(resource_id, owner_agent=owner_agent)
        except Exception:
            return False
