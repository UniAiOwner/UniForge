"""
UniMemory Database Engine
=========================
Manages SQLite connection pooling, WAL pragma enforcement,
and FTS5 full-text search synchronization.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from unimemory.config import BRAIN_MEMORY_DB, PRAGMAS


def get_db_connection(db_path: Optional[Path] = None, read_only: bool = False) -> sqlite3.Connection:
    target_path = Path(db_path) if db_path else BRAIN_MEMORY_DB
    conn = None

    if not read_only:
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(target_path), timeout=10.0)
        except (sqlite3.OperationalError, OSError):
            read_only = True

    if read_only:
        try:
            uri_str = f"{target_path.as_uri()}?mode=ro&immutable=1"
            conn = sqlite3.connect(uri_str, uri=True, timeout=10.0)
        except sqlite3.OperationalError:
            uri_str = f"{target_path.as_uri()}?mode=ro"
            conn = sqlite3.connect(uri_str, uri=True, timeout=10.0)

    conn.row_factory = sqlite3.Row

    # Apply performance pragmas
    cur = conn.cursor()
    for pragma_name, pragma_val in PRAGMAS.items():
        if read_only and pragma_name in ("journal_mode", "synchronous"):
            continue
        try:
            cur.execute(f"PRAGMA {pragma_name} = {pragma_val};")
        except sqlite3.OperationalError:
            pass

    return conn


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initializes tables, indexes, and FTS5 virtual search structures."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    cur.executescript("""
        -- Tier 1: Working Context Memory
        CREATE TABLE IF NOT EXISTS working_context (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL,
            project_scope TEXT NOT NULL DEFAULT 'GLOBAL',
            priority INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME
        );

        -- Tier 2: Episodic Memory & Failure Reflections (Law-STARK)
        CREATE TABLE IF NOT EXISTS episodic_ledger (
            episode_id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            goal TEXT NOT NULL,
            steps_json TEXT NOT NULL,
            errors_json TEXT NOT NULL,
            root_cause_lesson TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SUCCESS',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Tier 3: Bi-Temporal Semantic Knowledge Graph (Graphiti Standard)
        CREATE TABLE IF NOT EXISTS semantic_triplets (
            fact_id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
            valid_to DATETIME,
            is_current INTEGER NOT NULL DEFAULT 1
        );

        -- Tier 4: Codebase Symbols & AST Map (Zero-Guess VFS)
        CREATE TABLE IF NOT EXISTS codebase_symbols_vfs (
            symbol_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            symbol_name TEXT NOT NULL,
            symbol_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            doc_summary TEXT,
            symbol_hash TEXT,
            indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project, symbol_name, file_path, line_number)
        );

        -- Tier 0: Sovereign Cognitive Beacons (Living Mission Anchor & Anti-Drift Sentinel)
        CREATE TABLE IF NOT EXISTS cognitive_beacons (
            beacon_id TEXT PRIMARY KEY,
            mission_name TEXT NOT NULL,
            parent_goal TEXT NOT NULL,
            active_milestone TEXT NOT NULL,
            in_scope_paths_json TEXT NOT NULL,
            forbidden_domains_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Unified SQLite FTS5 Full-Text Index
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            doc_id,
            tier_name,
            entity_key,
            content_text,
            project,
            tokenize = 'porter unicode61'
        );

        -- Index for fast symbol lookups
        CREATE INDEX IF NOT EXISTS idx_symbols_name ON codebase_symbols_vfs(symbol_name);
        CREATE INDEX IF NOT EXISTS idx_symbols_project ON codebase_symbols_vfs(project);
        CREATE INDEX IF NOT EXISTS idx_triplets_subject ON semantic_triplets(subject, is_current);
        CREATE INDEX IF NOT EXISTS idx_triplets_object ON semantic_triplets(object, is_current);
        CREATE INDEX IF NOT EXISTS idx_episodic_project ON episodic_ledger(project, status);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_active_beacon ON cognitive_beacons(status) WHERE status = 'ACTIVE';
    """)

    conn.commit()
    return conn
