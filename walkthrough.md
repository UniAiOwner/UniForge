# ⬢ UniForge: Sovereign Autonomous Developer Suite Walkthrough

## 1. Overview
UniForge unites all 7 Sovereign Developer Services, the Sovereign Coding Triad, and the Deliberative Frontal Lobe under a single high-performance monorepo:
- **Location**: `/media/uniai/UniAi/PROJECTS_MIGRATED/UniForge/`
- **Master CLI**: `uniforge` (globally linked in `/home/uniai/.gemini/antigravity/bin/uniforge` and `~/.local/bin/uniforge`)
- **Version**: `v1.0.0`
- **Diagnostic Health**: 15/15 Pillars PASS (100% Green)
- **Automated Tests**: 202/202 Tests PASS (100% Green across all 9 packages)

## 2. Integrated Package Architecture
```
/media/uniai/UniAi/PROJECTS_MIGRATED/UniForge/
├── packages/
│   ├── unigov/              # Pillar 1: Sovereign Governance & Task DAG
│   ├── uniskill/            # Pillar 2: Skills Router & Token Economizer
│   ├── unimemory/           # Pillar 3: 5-Tier Holographic Living Memory
│   ├── univerify/           # Pillar 4: Z3 SMT Gatekeeper & Law-000 Guard
│   ├── uniexec/             # Pillar 5: bwrap Sandboxed Micro-Execution
│   ├── unibus/              # Pillar 6: Real-time IPC & File Work Mutex
│   ├── uniwatch/            # Pillar 7: Linux Inotify Sentinel & Watchdog
│   ├── sovereign_triad/     # Coding Triad (Python+Kotlin+Security)
│   └── deliberation/        # Deliberative Councils & MCTS Planner
├── src/uniforge/            # Master Suite Core (cli, doctor, workspace)
├── bin/uniforge             # Global CLI runner
├── pyproject.toml           # Monorepo editable configuration
├── Makefile                 # make install, test, doctor, status
├── README.md                # Sovereign documentation
└── dev_logs.txt             # Development audit log
```

## 3. Empirical Test Proof Across All 9 Packages

| Package | Test Module / Suite | Tests Run | Result | Duration |
| :--- | :--- | :--- | :--- | :--- |
| `unigov` | `packages/unigov/tests/` | 57 tests | **57 PASSED** | 35.94s |
| `uniskill` | `packages/uniskill/tests/` | 26 tests | **26 PASSED** | 1.23s |
| `unimemory` | `packages/unimemory/tests/` | 20 tests | **20 PASSED** | 1.10s |
| `univerify` | `packages/univerify/tests/` | 28 tests | **28 PASSED** | 0.51s |
| `uniexec` | `packages/uniexec/tests/` | 19 tests | **19 PASSED** | 5.56s |
| `unibus` | `packages/unibus/tests/` | 22 tests | **22 PASSED** | 3.33s |
| `uniwatch` | `packages/uniwatch/tests/` | 17 tests | **17 PASSED** | 0.58s |
| `triad` | `packages/sovereign_triad/` | 7 tests | **7 PASSED** | 0.49s |
| `deliberation` | `packages/deliberation/` | 6 tests | **6 PASSED** | 2.01s |
| **TOTAL** | **Full Suite Test Execution** | **202 tests** | **202 PASSED (100%)** | **50.75s** |

## 4. Master CLI Capabilities
1. `uniforge doctor`: Comprehensive diagnostic verifying packages, binaries, systemd, inotify, SQLite, bit-parity, MCP, memory, Z3 SMT, bwrap sandbox, and IPC.
2. `uniforge status [path]`: Live governance status, locked constraints, and execution DAG counts.
3. `uniforge init <path> -n <name> -o <objective>`: 1-click bootstrap for any target project.
4. `uniforge test [--package <pkg>]`: Runs unit and integration test suites.
5. `uniforge version`: Displays manifest and versions.
