"""
UniMemory Historical Migration Utility
======================================
Migrates legacy facts and decisions from fragmented databases
(ucmf_production.db, temporal_memory.db, ucgm_substrate.db)
into the single unified SQLite WAL database (~/.unicortex/brain_memory.db).
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from unimemory.db import get_db_connection, init_db
from unimemory.semantic import SemanticGraphManager
from unimemory.episodic import EpisodicMemoryManager


def migrate_legacy_databases(
    legacy_dir: Path = Path("/media/uniai/UniAi/PROJECTS_MIGRATED/Agentic team/02_UCMF_MEMORY"),
    dest_db: Optional[sqlite3.Connection] = None
) -> Dict[str, Any]:
    """Imports historical facts and decisions into the unified UniMemory substrate."""
    conn = dest_db or init_db()
    sem_mgr = SemanticGraphManager(conn)
    epi_mgr = EpisodicMemoryManager(conn)

    migrated_facts = 0
    migrated_episodes = 0
    errors = []

    # 1. Migrate ucmf_production.db
    ucmf_db = legacy_dir / "ucmf_production.db"
    if ucmf_db.exists():
        try:
            sconn = sqlite3.connect(str(ucmf_db))
            sconn.row_factory = sqlite3.Row
            scur = sconn.cursor()

            # Facts migration
            scur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ucmf_facts';")
            if scur.fetchone():
                scur.execute("SELECT topic, domain, canonical_statement, confidence_score FROM ucmf_facts WHERE status = 'ACTIVE' LIMIT 2000;")
                for r in scur.fetchall():
                    topic = r["topic"] or "Architecture"
                    domain = r["domain"] or "General"
                    stmt = r["canonical_statement"] or ""
                    conf = float(r["confidence_score"] or 1.0)
                    if stmt:
                        sem_mgr.add_fact(topic, f"belongs_to_{domain}", stmt, confidence=conf)
                        migrated_facts += 1

            # Decisions / Episodes migration
            scur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ucmf_decisions';")
            if scur.fetchone():
                scur.execute("SELECT project_id, title, problem_statement, chosen_option, rationale, status FROM ucmf_decisions LIMIT 500;")
                for r in scur.fetchall():
                    proj = r["project_id"] or "GLOBAL"
                    title = r["title"] or "Decision"
                    lesson = f"{r['chosen_option'] or ''}: {r['rationale'] or ''}"
                    status = r["status"] or "SUCCESS"
                    epi_mgr.record_episode(
                        project=proj,
                        goal=title,
                        steps_taken=[(r["problem_statement"] or "")[:150]],
                        errors_encountered=[],
                        root_cause_lesson=lesson[:300],
                        status=status
                    )
                    migrated_episodes += 1

            sconn.close()
        except Exception as e:
            errors.append(f"ucmf_production.db: {str(e)}")

    # 2. Migrate temporal_memory.db
    temporal_db = legacy_dir / "temporal_memory.db"
    if temporal_db.exists():
        try:
            tconn = sqlite3.connect(str(temporal_db))
            tconn.row_factory = sqlite3.Row
            tcur = tconn.cursor()
            tcur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='temporal_facts';")
            if tcur.fetchone():
                tcur.execute("SELECT entity, attribute, value, confidence FROM temporal_facts WHERE status = 'ACTIVE' LIMIT 1000;")
                for r in tcur.fetchall():
                    s, p, o = r["entity"], r["attribute"], r["value"]
                    if s and p and o:
                        sem_mgr.add_fact(s, p, o, confidence=float(r["confidence"] or 1.0))
                        migrated_facts += 1
            tconn.close()
        except Exception as e:
            errors.append(f"temporal_memory.db: {str(e)}")

    # 3. Migrate ucgm_substrate.db edges
    ucgm_db = legacy_dir / "ucgm_substrate.db"
    if ucgm_db.exists():
        try:
            uconn = sqlite3.connect(str(ucgm_db))
            uconn.row_factory = sqlite3.Row
            ucur = uconn.cursor()
            ucur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ucgm_edges';")
            if ucur.fetchone():
                ucur.execute("SELECT from_id, relation_type, to_id, weight FROM ucgm_edges LIMIT 2000;")
                for r in ucur.fetchall():
                    s, p, o = r["from_id"], r["relation_type"], r["to_id"]
                    if s and p and o:
                        sem_mgr.add_fact(s, p, o, confidence=float(r["weight"] or 1.0))
                        migrated_facts += 1
            uconn.close()
        except Exception as e:
            errors.append(f"ucgm_substrate.db: {str(e)}")

    return {
        "status": "SUCCESS" if not errors else "PARTIAL",
        "migrated_facts": migrated_facts,
        "migrated_episodes": migrated_episodes,
        "errors": errors
    }
