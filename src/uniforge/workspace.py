"""UniForge Workspace Manager.

Provides 1-click sovereign workspace initialization, status aggregation,
and drift detection for any target project.
"""

import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from rich.console import Console

console = Console()

from unigov.db import init_workspace_folders, get_db, resolve_gov_dir


def init_workspace(
    project_path: Path,
    project_name: str,
    objective: str,
    constraints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Initializes a target directory as a sovereign UniForge / UniGov workspace."""
    abs_path = project_path.resolve()
    abs_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Initialize .unigov governance folders
    gov_dir = init_workspace_folders(abs_path)
    
    # 2. Initialize state.db and project_vision table
    conn = get_db(abs_path, require_init=False)
    
    hard_constraints = constraints or [
        "Constitutional Law-000: Zero Shortcuts, Zero @Suppress allowed.",
        "Law ACC-001: 64-Bit Integer Paise Math using Long (Zero floating point math).",
        "Universal Portability: Zero hardcoded project paths; dynamic relative workspace resolution.",
    ]
    
    conn.execute(
        "INSERT OR REPLACE INTO project_vision (id, project_name, core_objective, hard_constraints_json) VALUES (1, ?, ?, ?)",
        (project_name, objective, json.dumps(hard_constraints))
    )
    conn.commit()
    conn.close()
    
    # 3. Install git pre-commit drift hook if git repo exists
    git_dir = abs_path / ".git"
    hook_installed = False
    if git_dir.exists():
        try:
            hook_path = git_dir / "hooks" / "pre-commit"
            hook_path.parent.mkdir(parents=True, exist_ok=True)
            script = """#!/bin/sh
# ⬢ UniGov & UniSkill Sovereign Dual Invariant Pre-Commit Gate
set -e

# 1. UniGov Drift Check
if command -v unigov >/dev/null 2>&1; then
    unigov check-drift --staged
fi

# 2. UniSkill Constitutional Invariants Audit
if command -v uniskill >/dev/null 2>&1; then
    uniskill audit
fi

echo "✔ Pre-commit Gate Passed: Clean Architecture & 0-Suppress Invariants."
"""
            hook_path.write_text(script, encoding="utf-8")
            hook_path.chmod(0o755)
            hook_installed = True
        except Exception:
            pass

    return {
        "status": "INITIALIZED",
        "project_name": project_name,
        "project_path": str(abs_path),
        "gov_dir": str(gov_dir),
        "hard_constraints": hard_constraints,
        "git_hook_installed": hook_installed,
    }


def get_workspace_status(project_path: Path) -> Dict[str, Any]:
    """Aggregates status from UniGov, UniMemory, and UniWatch for the target project."""
    abs_path = project_path.resolve()
    gov_dir = resolve_gov_dir(abs_path)
    db_file = gov_dir / "state.db"
    
    if not db_file.exists():
        return {
            "status": "UNINITIALIZED",
            "project_path": str(abs_path),
            "message": f"Workspace not initialized at {abs_path}. Run 'uniforge init' first.",
        }
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        vision_row = conn.execute("SELECT project_name, core_objective, hard_constraints_json FROM project_vision WHERE id = 1").fetchone()
        if not vision_row:
            return {"status": "UNINITIALIZED", "project_path": str(abs_path)}
        
        task_rows = conn.execute("SELECT status, count(*) as cnt FROM tasks GROUP BY status").fetchall()
        counts = {r["status"]: r["cnt"] for r in task_rows}
        
        return {
            "status": "INITIALIZED",
            "project_name": vision_row["project_name"],
            "core_objective": vision_row["core_objective"],
            "hard_constraints": json.loads(vision_row["hard_constraints_json"] or "[]"),
            "task_counts": counts,
            "project_path": str(abs_path),
        }
    finally:
        conn.close()
