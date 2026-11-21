"""
UniMemory Tier 4: Codebase Symbols & AST Map (Zero-Guess VFS)
=============================================================
Provides sub-millisecond symbol lookup across all projects,
eliminating file-path hallucination and ad-hoc searches.
"""

import os
import re
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from unimemory.db import get_db_connection
from unimemory.models import SymbolItem

# AST Symbol Extraction Regexes
SYMBOL_PATTERNS = {
    "composable": re.compile(r"@Composable\s+fun\s+([A-Za-z0-9_]+)"),
    "entity": re.compile(r"@Entity(?:\([^)]*\))?\s+(?:data\s+)?class\s+([A-Za-z0-9_]+)"),
    "class": re.compile(r"\b(?:class|interface|data\s+class|sealed\s+class|enum\s+class)\s+([A-Za-z0-9_]+)"),
    "function": re.compile(r"\b(?:fun|def|fn|async\s+def)\s+([A-Za-z0-9_]+)"),
}


class CodebaseVFSManager:

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self._conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return get_db_connection()

    def index_project(
        self,
        project_name: str,
        project_path: Path,
        max_files: int = 500
    ) -> Dict[str, Any]:
        """Indexes source code symbols across a project root into SQLite VFS."""
        p_path = Path(project_path)
        if not p_path.exists():
            return {"status": "ERROR", "error": f"Path does not exist: {project_path}"}

        conn = self._get_conn()
        cur = conn.cursor()

        valid_extensions = {".kt", ".py", ".rs", ".ts", ".js", ".sql"}
        ignore_dirs = {".git", ".gradle", "build", "node_modules", ".idea", ".unigov", "__pycache__", "dist"}

        total_files = 0
        symbols_indexed = 0
        now_str = datetime.now(timezone.utc).isoformat()

        # Clean existing symbols for this project to ensure freshness
        cur.execute("DELETE FROM codebase_symbols_vfs WHERE project = ?", (project_name,))
        cur.execute("DELETE FROM memory_fts WHERE tier_name = 'symbol' AND project = ?", (project_name,))

        for root, dirs, files in os.walk(str(p_path)):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in valid_extensions:
                    continue

                full_path = Path(root) / file
                rel_path = str(full_path.relative_to(p_path))
                total_files += 1

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                pending_annotation = None
                for line_idx, line in enumerate(lines):
                    trimmed = line.strip()
                    if not trimmed or trimmed.startswith(("//", "#", "/*", "*")):
                        continue

                    # Capture single-line annotations
                    if trimmed.startswith("@Composable"):
                        pending_annotation = "composable"
                    elif trimmed.startswith("@Entity"):
                        pending_annotation = "entity"

                    matched_sym = False
                    for sym_type, regex in SYMBOL_PATTERNS.items():
                        m = regex.search(trimmed)
                        if m:
                            actual_type = sym_type
                            if sym_type == "function" and pending_annotation == "composable":
                                actual_type = "composable"
                            elif sym_type == "class" and pending_annotation == "entity":
                                actual_type = "entity"

                            sym_name = m.group(1)
                            sym_hash = hashlib.md5(f"{rel_path}:{line_idx}:{sym_name}".encode()).hexdigest()[:8]

                            cur.execute("""
                                INSERT OR IGNORE INTO codebase_symbols_vfs (
                                    project, symbol_name, symbol_type, file_path, line_number, doc_summary, symbol_hash, indexed_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                project_name, sym_name, actual_type, rel_path, line_idx + 1, trimmed[:200], sym_hash, now_str
                            ))

                            # Sync to FTS5
                            doc_id = f"sym_{project_name}_{sym_name}_{line_idx+1}"
                            content_text = f"{actual_type} {sym_name} in {rel_path} : {trimmed}"
                            cur.execute("""
                                INSERT INTO memory_fts (doc_id, tier_name, entity_key, content_text, project)
                                VALUES (?, 'symbol', ?, ?, ?)
                            """, (doc_id, sym_name, content_text, project_name))

                            symbols_indexed += 1
                            matched_sym = True
                            pending_annotation = None
                            break

                    if not matched_sym and not trimmed.startswith("@"):
                        pending_annotation = None

                if total_files >= max_files:
                    break
            if total_files >= max_files:
                break

        conn.commit()
        return {
            "status": "SUCCESS",
            "project": project_name,
            "files_scanned": total_files,
            "symbols_indexed": symbols_indexed
        }

    def search_symbols(
        self,
        query: str,
        project: Optional[str] = None,
        limit: int = 10
    ) -> List[SymbolItem]:
        """Sub-millisecond lookup for classes, composables, or functions."""
        conn = self._get_conn()
        cur = conn.cursor()

        clean_q = "".join(c if c.isalnum() or c == "_" else " " for c in query).strip()
        if not clean_q:
            return []

        # Try exact/prefix match on symbol_name first
        sql = """
            SELECT project, symbol_name, symbol_type, file_path, line_number, doc_summary, symbol_hash
            FROM codebase_symbols_vfs
            WHERE symbol_name LIKE ?
        """
        params: List[Any] = [f"%{clean_q}%"]
        if project:
            sql += " AND project = ?"
            params.append(project)

        sql += " ORDER BY CASE WHEN symbol_name = ? THEN 0 ELSE 1 END, line_number ASC LIMIT ?"
        params.extend([clean_q, limit])

        cur.execute(sql, params)
        rows = cur.fetchall()

        return [
            SymbolItem(
                project=r["project"],
                symbol_name=r["symbol_name"],
                symbol_type=r["symbol_type"],
                file_path=r["file_path"],
                line_number=r["line_number"],
                doc_summary=r["doc_summary"] or "",
                symbol_hash=r["symbol_hash"] or ""
            )
            for r in rows
        ]
