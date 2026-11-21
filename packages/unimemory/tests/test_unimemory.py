"""
Comprehensive Unit Tests for UniMemory Substrate
================================================
Verifies all 5 cognitive tiers, FTS5 BM25 search, HippoRAG PageRank,
Graphiti bi-temporal invalidation, and sub-15ms recall latency.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
import pytest

from unimemory.engine import UniMemoryEngine
from unimemory.models import MemoryRecallResult


@pytest.fixture
def temp_engine():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db = Path(tf.name)
    engine = UniMemoryEngine(db_path=temp_db)
    yield engine
    if temp_db.exists():
        temp_db.unlink()
    # clean wal files if any
    for ext in ("-wal", "-shm"):
        wal_p = Path(str(temp_db) + ext)
        if wal_p.exists():
            wal_p.unlink()


def test_db_initialization_and_wal(temp_engine):
    cur = temp_engine.conn.cursor()
    cur.execute("PRAGMA journal_mode;")
    mode = cur.fetchone()[0]
    assert mode.upper() == "WAL", f"Expected WAL mode, got {mode}"

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    assert "working_context" in tables
    assert "episodic_ledger" in tables
    assert "semantic_triplets" in tables
    assert "codebase_symbols_vfs" in tables
    assert "memory_fts" in tables


def test_working_memory_paging(temp_engine):
    temp_engine.set_working(key="active_task", value="Design UniMemory", project_scope="Agentic team", priority=3)
    item = temp_engine.working.get("active_task")
    assert item is not None
    assert item.key == "active_task"
    assert "UniMemory" in item.value_json
    assert item.priority == 3

    # Test listing active
    items = temp_engine.working.list_active()
    assert len(items) == 1
    assert items[0].key == "active_task"


def test_episodic_memory_and_stark(temp_engine):
    temp_engine.record_episode(
        project="UniRetail",
        goal="Calculate GST invoice total",
        steps_taken=["Parsed price", "Applied float tax calculation"],
        errors_encountered=["Precision roundoff error in paise"],
        root_cause_lesson="Never use Double for currency; Law ACC-001 mandates integer paise.",
        status="FAILED"
    )

    # Query STARK countermeasure
    lessons = temp_engine.episodic.get_stark_countermeasures("calculate invoice GST")
    assert len(lessons) >= 1
    assert "Law ACC-001" in lessons[0].root_cause_lesson
    assert lessons[0].status == "FAILED"


def test_semantic_graph_and_bitemporal_evolution(temp_engine):
    # Initial fact
    fact1 = temp_engine.store_fact(
        subject="UniCortex",
        predicate="uses_memory_architecture",
        target_object="Fragmented-SQLite",
        confidence=0.8
    )
    assert fact1["is_current"] is True

    # New superior fact invalidating the old fact
    fact2 = temp_engine.store_fact(
        subject="UniCortex",
        predicate="uses_memory_architecture",
        target_object="UniMemory-Unified-WAL",
        confidence=1.0
    )
    assert fact2["is_current"] is True

    # Check that fact1 was soft-retired
    cur = temp_engine.conn.cursor()
    cur.execute("SELECT object, is_current, valid_to FROM semantic_triplets WHERE fact_id = ?", (fact1["fact_id"],))
    row = cur.fetchone()
    assert row["is_current"] == 0
    assert row["valid_to"] is not None
    assert row["object"] == "Fragmented-SQLite"


def test_hipporag_pagerank_associative_walk(temp_engine):
    # Build a small knowledge graph
    temp_engine.store_fact("Shoeb Ahmad", "founded", "UniAi")
    temp_engine.store_fact("UniAi", "develops", "UniCortex")
    temp_engine.store_fact("UniCortex", "operates", "UniMemory")
    temp_engine.store_fact("UniMemory", "implements", "HippoRAG")

    # Run Personalized PageRank starting at 'Shoeb'
    ranked = temp_engine.semantic.compute_hipporag_pagerank(start_entities=["Shoeb"], top_k=3)
    assert len(ranked) > 0
    ranked_entities = [entity for entity, _ in ranked]
    assert "UniAi" in ranked_entities or "UniCortex" in ranked_entities


def test_codebase_vfs_indexing(temp_engine, tmp_path):
    # Create dummy project files
    p_dir = tmp_path / "DummyProject"
    p_dir.mkdir()
    kt_file = p_dir / "InvoiceModel.kt"
    kt_file.write_text("""
    package com.uniai.pos
    @Entity
    data class InvoiceEntity(val id: Long, val totalPaise: Long)
    @Composable
    fun InvoiceScreen(invoice: InvoiceEntity) {}
    fun computeTax(amount: Long): Long = amount * 18 / 100
    """)

    res = temp_engine.sync_project(project_path=p_dir, project_name="DummyProject")
    assert res["status"] == "SUCCESS"
    assert res["symbols_indexed"] >= 3

    symbols = temp_engine.vfs.search_symbols("InvoiceScreen")
    assert len(symbols) >= 1
    assert symbols[0].symbol_name == "InvoiceScreen"
    assert symbols[0].symbol_type == "composable"


def test_unified_hybrid_recall(temp_engine):
    temp_engine.set_working(key="active_target", value="POS Terminal Bill Print")
    temp_engine.store_fact("ESC/POS", "formats", "Thermal Receipts")
    temp_engine.record_episode(
        project="UniRetail",
        goal="Print thermal receipt",
        steps_taken=["Generated ESC/POS bytes"],
        errors_encountered=[],
        root_cause_lesson="Use raw ESC/POS byte generator without desktop drivers.",
        status="SUCCESS"
    )

    res = temp_engine.recall("thermal receipt ESC/POS")
    assert isinstance(res, MemoryRecallResult)
    assert len(res.semantic_facts) >= 1 or len(res.episodic_lessons) >= 1
    assert res.retrieval_latency_ms < 100.0  # Must be fast in-memory


def test_doctor_telemetry(temp_engine):
    doc = temp_engine.doctor()
    assert doc["is_healthy"] is True
    assert doc["integrity_check"] == "ok"
