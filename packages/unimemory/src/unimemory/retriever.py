"""
UniMemory Unified Hybrid Retriever
==================================
Combines BM25 FTS5 lexical ranking, bi-temporal knowledge graph traversal,
HippoRAG 2 Personalized PageRank, and active working context paging.
"""

import time
import sqlite3
from typing import Dict, Any, List, Optional
from unimemory.db import get_db_connection
from unimemory.working import WorkingMemoryManager
from unimemory.episodic import EpisodicMemoryManager
from unimemory.semantic import SemanticGraphManager
from unimemory.codebase_vfs import CodebaseVFSManager
from unimemory.models import MemoryRecallResult, WorkingMemoryItem, EpisodicEntry, SemanticFact, SymbolItem


class UnifiedRetriever:

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self._conn = db_conn or get_db_connection()
        self.working_mgr = WorkingMemoryManager(self._conn)
        self.episodic_mgr = EpisodicMemoryManager(self._conn)
        self.semantic_mgr = SemanticGraphManager(self._conn)
        self.vfs_mgr = CodebaseVFSManager(self._conn)

    def recall(
        self,
        query: str,
        project_scope: Optional[str] = None,
        top_k: int = 5
    ) -> MemoryRecallResult:
        """
        Executes an end-to-end multi-tier hybrid recall in < 15ms.
        """
        start_t = time.perf_counter()

        # 1. Tier 1: Check active working context
        active_working = self.working_mgr.list_active(project_scope=project_scope, limit=10)
        matched_working: List[WorkingMemoryItem] = []
        q_lower = query.lower()
        for w in active_working:
            if w.key.lower() in q_lower or any(word in w.value_json.lower() for word in q_lower.split() if len(word) > 2):
                matched_working.append(w)

        # 2. Tier 2: FTS5 BM25 search across all tiers
        cur = self._conn.cursor()
        clean_tokens = [t for t in query.split() if len(t) >= 2][:5]
        fts_hits: Dict[str, List[str]] = {"episodic": [], "semantic": [], "symbol": []}

        if clean_tokens:
            fts_expr = " OR ".join(f'"{t}"*' for t in clean_tokens)
            sql = """
                SELECT doc_id, tier_name, bm25(memory_fts) as rank
                FROM memory_fts
                WHERE memory_fts MATCH ?
            """
            params: List[Any] = [fts_expr]
            if project_scope and project_scope != "GLOBAL":
                sql += " AND (project = ? OR project = 'GLOBAL')"
                params.append(project_scope)

            sql += " ORDER BY rank LIMIT 30;"

            try:
                cur.execute(sql, params)
                for row in cur.fetchall():
                    tier = row["tier_name"]
                    if tier in fts_hits:
                        fts_hits[tier].append(row["doc_id"])
            except Exception:
                pass

        # 3. Retrieve Episodic Entries
        matched_episodes: List[EpisodicEntry] = []
        if fts_hits["episodic"]:
            placeholders = ",".join("?" for _ in fts_hits["episodic"][:top_k])
            cur.execute(f"""
                SELECT episode_id, project, goal, steps_json, errors_json, root_cause_lesson, status, created_at
                FROM episodic_ledger
                WHERE episode_id IN ({placeholders})
                ORDER BY created_at DESC;
            """, fts_hits["episodic"][:top_k])

            import json
            for r in cur.fetchall():
                matched_episodes.append(EpisodicEntry(
                    episode_id=r["episode_id"],
                    project=r["project"],
                    goal=r["goal"],
                    steps_taken=json.loads(r["steps_json"]),
                    errors_encountered=json.loads(r["errors_json"]),
                    root_cause_lesson=r["root_cause_lesson"],
                    status=r["status"],
                    created_at=str(r["created_at"])
                ))

        # 4. Retrieve Semantic Facts & Run HippoRAG PageRank
        matched_facts: List[SemanticFact] = []
        if fts_hits["semantic"]:
            placeholders = ",".join("?" for _ in fts_hits["semantic"][:top_k])
            cur.execute(f"""
                SELECT fact_id, subject, predicate, object, confidence, valid_from, valid_to, is_current
                FROM semantic_triplets
                WHERE fact_id IN ({placeholders}) AND is_current = 1
                ORDER BY confidence DESC;
            """, fts_hits["semantic"][:top_k])

            for r in cur.fetchall():
                matched_facts.append(SemanticFact(
                    fact_id=r["fact_id"],
                    subject=r["subject"],
                    predicate=r["predicate"],
                    object=r["object"],
                    confidence=r["confidence"],
                    valid_from=str(r["valid_from"]),
                    valid_to=str(r["valid_to"]) if r["valid_to"] else None,
                    is_current=bool(r["is_current"])
                ))

        # Run associative HippoRAG PageRank if query has recognized entities
        if clean_tokens:
            associative_nodes = self.semantic_mgr.compute_hipporag_pagerank(
                start_entities=clean_tokens,
                top_k=3
            )
            for assoc_entity, score in associative_nodes:
                extra_facts = self.semantic_mgr.query_facts(assoc_entity, is_current_only=True, limit=2)
                for ef in extra_facts:
                    if ef.fact_id not in [f.fact_id for f in matched_facts]:
                        matched_facts.append(ef)

        # 5. Retrieve Codebase Symbols
        matched_symbols: List[SymbolItem] = []
        if fts_hits["symbol"]:
            # Direct symbol search fallback
            matched_symbols = self.vfs_mgr.search_symbols(query, project=project_scope, limit=top_k)
        elif not matched_symbols and clean_tokens:
            matched_symbols = self.vfs_mgr.search_symbols(clean_tokens[0], project=project_scope, limit=top_k)

        latency = (time.perf_counter() - start_t) * 1000.0

        return MemoryRecallResult(
            query=query,
            working_context=matched_working[:top_k],
            episodic_lessons=matched_episodes[:top_k],
            semantic_facts=matched_facts[:top_k],
            codebase_symbols=matched_symbols[:top_k],
            retrieval_latency_ms=round(latency, 2)
        )
