"""
UniMemory Tier 3: Bi-Temporal Semantic Knowledge Graph
======================================================
Implements Graphiti bi-temporal edge evolution (valid_from / valid_to)
and HippoRAG 2 Personalized PageRank (PPR) associative multi-hop retrieval.
"""

import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timezone
from unimemory.db import get_db_connection
from unimemory.models import SemanticFact


class SemanticGraphManager:

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self._conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return get_db_connection()

    def add_fact(
        self,
        subject: str,
        predicate: str,
        target_object: str,
        confidence: float = 1.0,
        fact_id: Optional[str] = None
    ) -> SemanticFact:
        """
        Adds a semantic fact. If an older fact with identical (subject, predicate)
        exists with a different target_object, it is soft-retired (is_current=0, valid_to=now).
        """
        conn = self._get_conn()
        cur = conn.cursor()

        now_str = datetime.now(timezone.utc).isoformat()
        if not fact_id:
            raw = f"{subject}:{predicate}:{target_object}:{now_str}"
            fact_id = f"fact_{hashlib.sha256(raw.encode()).hexdigest()[:12]}"

        # Graphiti Invariant: Soft-retire obsolete conflicting facts
        cur.execute("""
            UPDATE semantic_triplets
            SET is_current = 0, valid_to = ?
            WHERE subject = ? AND predicate = ? AND object != ? AND is_current = 1;
        """, (now_str, subject, predicate, target_object))

        # Insert new active fact
        cur.execute("""
            INSERT OR REPLACE INTO semantic_triplets (
                fact_id, subject, predicate, object, confidence, valid_from, valid_to, is_current
            ) VALUES (?, ?, ?, ?, ?, ?, NULL, 1)
        """, (fact_id, subject, predicate, target_object, confidence, now_str))

        # Sync to FTS5
        content_text = f"{subject} {predicate} {target_object}"
        cur.execute("DELETE FROM memory_fts WHERE doc_id = ? AND tier_name = 'semantic'", (fact_id,))
        cur.execute("""
            INSERT INTO memory_fts (doc_id, tier_name, entity_key, content_text, project)
            VALUES (?, 'semantic', ?, ?, 'GLOBAL')
        """, (fact_id, subject, content_text))

        conn.commit()

        return SemanticFact(
            fact_id=fact_id,
            subject=subject,
            predicate=predicate,
            object=target_object,
            confidence=confidence,
            valid_from=now_str,
            valid_to=None,
            is_current=True
        )

    def query_facts(
        self,
        entity: str,
        is_current_only: bool = True,
        limit: int = 10
    ) -> List[SemanticFact]:
        """Queries facts where entity is either the subject or the object."""
        conn = self._get_conn()
        cur = conn.cursor()

        condition = "AND is_current = 1" if is_current_only else ""
        sql = f"""
            SELECT fact_id, subject, predicate, object, confidence, valid_from, valid_to, is_current
            FROM semantic_triplets
            WHERE (subject LIKE ? OR object LIKE ?) {condition}
            ORDER BY confidence DESC, valid_from DESC
            LIMIT ?
        """
        wildcard = f"%{entity.strip()}%"
        cur.execute(sql, (wildcard, wildcard, limit))

        return [
            SemanticFact(
                fact_id=r["fact_id"],
                subject=r["subject"],
                predicate=r["predicate"],
                object=r["object"],
                confidence=r["confidence"],
                valid_from=str(r["valid_from"]),
                valid_to=str(r["valid_to"]) if r["valid_to"] else None,
                is_current=bool(r["is_current"])
            )
            for r in cur.fetchall()
        ]

    def compute_hipporag_pagerank(
        self,
        start_entities: List[str],
        damping: float = 0.85,
        iterations: int = 10,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Computes Personalized PageRank (HippoRAG 2) across the current knowledge graph.
        Returns the top associative entities discovered via multi-hop paths.
        """
        conn = self._get_conn()
        cur = conn.cursor()

        # Fetch all active edges
        cur.execute("SELECT subject, object, confidence FROM semantic_triplets WHERE is_current = 1;")
        edges = cur.fetchall()

        if not edges:
            return []

        # Build adjacency graph
        adj: Dict[str, List[Tuple[str, float]]] = {}
        all_nodes: Set[str] = set()

        for r in edges:
            u, v, w = r["subject"], r["object"], r["confidence"]
            all_nodes.add(u)
            all_nodes.add(v)
            adj.setdefault(u, []).append((v, w))
            adj.setdefault(v, []).append((u, w))  # Undirected propagation for associative retrieval

        if not all_nodes:
            return []

        # Initialize restart vector
        p0: Dict[str, float] = {node: 0.0 for node in all_nodes}
        matched_starts = [node for node in all_nodes if any(s.lower() in node.lower() for s in start_entities)]

        if not matched_starts:
            # Fallback uniform
            p0 = {node: 1.0 / len(all_nodes) for node in all_nodes}
        else:
            weight = 1.0 / len(matched_starts)
            for s in matched_starts:
                p0[s] = weight

        # Power Iteration
        p = dict(p0)
        for _ in range(iterations):
            p_next: Dict[str, float] = {node: (1.0 - damping) * p0[node] for node in all_nodes}
            for u, neighbors in adj.items():
                if not neighbors or p[u] == 0:
                    continue
                deg = sum(w for _, w in neighbors)
                for v, w in neighbors:
                    p_next[v] += damping * p[u] * (w / deg)
            p = p_next

        # Filter out input entities and sort by score
        ranked = [
            (node, score) for node, score in p.items()
            if node not in matched_starts
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
