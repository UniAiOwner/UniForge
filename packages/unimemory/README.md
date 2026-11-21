# UniMemory: Sovereign Cognitive Memory Substrate

UniMemory is the unified, high-performance, 5-tier living memory engine of the UniCortex Cognitive Architecture.

## Architectural Tiers
1. **Working Context Paging**: Immediate turn-by-turn memory and active task cache.
2. **Episodic Memory**: Task histories, empirical outcomes, and failure reflections (enforcing Law-STARK).
3. **Semantic Knowledge Graph**: Bi-temporal entity-relation-target facts with validity ranges and automated edge evolution.
4. **Codebase Symbol VFS**: High-speed AST symbol extraction and mapping for sub-millisecond symbol lookup.
5. **Procedural Invariants**: Hard rules, zero-shortcut invariants (Law-000), and financial rules (Law ACC-001 Integer Paise).

## Storage Engine
- **Single Unified Database**: `~/.unicortex/brain_memory.db` (SQLite in WAL mode).
- **Fast Full-Text Search**: SQLite FTS5 with BM25 ranking.
- **Associative Multi-Hop**: Personalized PageRank (HippoRAG 2) graph navigation.

## Usage
```bash
# Multi-tier memory recall
unimemory recall "accounting double entry paise"

# Store an episodic lesson or semantic fact
unimemory store "Law ACC-001 mandates integer paise across all transaction models" --type semantic

# Sync codebase symbols and project state
unimemory sync "/path/to/project"

# Comprehensive health check
unimemory doctor
```
