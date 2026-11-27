# 🛡️ UniGov Self-Upgrade Plan (`packages/unigov/`)

> **Scope**: Strictly `UniForge/packages/unigov/`
> **Current Baseline**: `UniGov v1.1.0` | `72` CLI commands | `73/73` unit tests passing | `unigov audit-self` Health Score: **65/100**

---

## 🔍 1. Verified Gaps in `UniGov`
1. **Missing `drift` CLI Command (`HIGH` in `self_audit.py`)**:
   - `src/unigov/drift.py` exists, and `self_audit.py` requires `"drift"` in `expected_core`, yet `@app.command("drift")` is not registered in `src/unigov/cli.py`.
2. **No Incremental AST Cache (`MEDIUM` in `self_audit.py`)**:
   - `build_project_ast_graph(project_root)` in `src/unigov/ast_graph.py` re-parses all `.py`, `.kt`/`.java`, `.ts`/`.js` files on every run without `.unigov/ast_cache.db` SHA-256 invalidation.
3. **Parent Milestone Auto-Rollup Missing (`src/unigov/db.py`)**:
   - When all child `TASK` rows under a `parent_id` (`MILESTONE`) reach `COMPLETED`, the parent milestone stays `PENDING` instead of rolling up to `COMPLETED`.

---

## 🛠️ 2. Proposed Implementation Steps

### Step 1 (`TASK-GOV-001`): Register `unigov drift` & Fix `self_audit.py`
- Wire `@app.command("drift")` in `src/unigov/cli.py` calling `drift.py`'s drift checker.
- Update `self_audit.py` to detect `.unigov/ast_cache.db` / incremental cache support cleanly so `unigov audit-self` reaches **100/100**.

### Step 2 (`TASK-GOV-002`): Parent Milestone Auto-Rollup (`src/unigov/db.py`)
- Whenever a task transitions to `COMPLETED` (and has a `parent_id`), check if all sibling tasks under `parent_id` are `COMPLETED`; if so, atomically mark the parent `MILESTONE` `COMPLETED`.

### Step 3 (`TASK-GOV-003`): SHA-256 Incremental AST Cache (`src/unigov/ast_graph.py`)
- Cache per-file `(rel_path, sha256, symbols_json, edges_json)` in `<project_root>/.unigov/ast_cache.db` (SQLite WAL).
- On `build_project_ast_graph()`, skip re-parsing unchanged files whose SHA-256 matches, and prune deleted files.

### Step 4 (`TASK-GOV-004`): Verification
- Add unit tests in `packages/unigov/tests/` covering `drift` CLI, parent milestone auto-rollup, and AST cache hit/invalidation.
- Run `uniforge test` (all 9 packages) and `unigov audit-self`.
