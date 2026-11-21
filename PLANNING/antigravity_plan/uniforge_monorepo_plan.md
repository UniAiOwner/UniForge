# UniForge: Sovereign Developer Suite Monorepo Architecture

## 1. Executive Overview
UniForge is the unified monorepo suite consolidating all 7 Sovereign Developer Services, the Sovereign Coding Triad, and the Frontal Lobe Deliberative Engine under a single high-performance repository at `/media/uniai/UniAi/PROJECTS_MIGRATED/UniForge/`.

### 9 Integrated Components:
1. **packages/unigov**: Sovereign Project Governance, Task DAG, Invariant Enforcement & Drift Reconciler.
2. **packages/uniskill**: Surgical Skills Router, Zero-Noise Token Economizer & Parity Engine.
3. **packages/unimemory**: 5-Tier Holographic Living Memory Substrate & HippoRAG 2 Graph.
4. **packages/univerify**: 4-Tier Deterministic Code Verification Gatekeeper (Z3 SMT + Law-000 Guard).
5. **packages/uniexec**: Sandboxed Code-Mode Micro-Execution Runtime (`bwrap` + `prlimit`).
6. **packages/unibus**: High-Throughput IPC & Work-Mutex Mutex Bus (Unix Domain Sockets + WAL).
7. **packages/uniwatch**: Real-Time Linux Inotify Sentinel & Continuous AST Integrity Watchdog.
8. **packages/triad**: Sovereign Coding Triad (Python + Kotlin + Security Specialist Council).
9. **packages/deliberation**: Frontal Lobe Deliberative Engine (5 Specialized Councils + MCTS Planner).

## 2. Directory Layout
```
/media/uniai/UniAi/PROJECTS_MIGRATED/UniForge/
├── packages/
│   ├── unigov/
│   ├── uniskill/
│   ├── unimemory/
│   ├── univerify/
│   ├── uniexec/
│   ├── unibus/
│   ├── uniwatch/
│   ├── triad/
│   └── deliberation/
├── src/
│   └── uniforge/
│       ├── __init__.py
│       ├── cli.py
│       ├── doctor.py
│       └── workspace.py
├── bin/
│   └── uniforge
├── pyproject.toml
├── Makefile
├── README.md
├── dev_logs.txt
└── walkthrough.md
```

## 3. Master CLI: `uniforge`
- `uniforge doctor`: Comprehensive 13-pillar system diagnostic.
- `uniforge status [path]`: Holistic project status (Governance + Memory + Watcher).
- `uniforge init <path> --name <name> --objective <obj>`: 1-click sovereign workspace bootstrap.
- `uniforge test`: Unified test runner across all 9 packages.
- `uniforge version`: Manifest and package parity status.
