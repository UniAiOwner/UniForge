<div align="center">

```text
  _    _       _ ______
 | |  | |     (_)  ____|
 | |  | |_ __  _| |__ ___  _ __ __ _  ___
 | |  | | '_ \| |  __/ _ \| '__/ _` |/ _ \
 | |__| | | | | | | | (_) | | | (_| |  __/
  \____/|_| |_|_|_|  \___/|_|  \__, |\___|
                                __/ |
                               |___/
```

### **Sovereign Autonomous Developer Suite & Engineering Machine**

[![Version](https://img.shields.io/badge/Version-1.0.0-emerald?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge)]()
[![Pillars](https://img.shields.io/badge/Integrated_Pillars-9-0ea5e9?style=for-the-badge)]()
[![UniGov](https://img.shields.io/badge/UniGov-2.0_Chief_Architect-8b5cf6?style=for-the-badge)]()

*Consolidating 7 Sovereign Developer Services, the Sovereign Coding Triad, and the Frontal Lobe Deliberative Engine into one unified CLI and monorepo.*

</div>

---

## Architecture Overview

```text
+-----------------------------------------------------------------------------+
|                           UNIFORGE MASTER CLI                               |
|        uniforge activate | doctor | status | init | test | version          |
+-----------------------------------------------------------------------------+
       |                    |                    |                    |
       v                    v                    v                    v
+--------------+    +---------------+    +---------------+    +---------------+
|   UNIGOV     |    |   UNISKILL    |    |   UNIMEMORY   |    |   UNIVERIFY   |
| Task DAG &   |    | Skill Router  |    | 5-Tier Living |    | Z3 SMT Proofs |
| 5 Organs 2.0 |    | Token Saver   |    | HippoRAG 2 DB |    | Law-000 Guard |
+--------------+    +---------------+    +---------------+    +---------------+
       |                    |                    |                    |
       v                    v                    v                    v
+--------------+    +---------------+    +---------------+    +---------------+
|   UNIEXEC    |    |    UNIBUS     |    |   UNIWATCH    |    |     TRIAD     |
| Bubblewrap   |    | UDS IPC &     |    | Inotify AST   |    | Python/Kotlin |
| Sandbox Run  |    | File Mutexes  |    | Sentinel      |    | Security Team |
+--------------+    +---------------+    +---------------+    +---------------+
                                    |
                                    v
                     +-----------------------------+
                     |    DELIBERATION ENGINE      |
                     | 5 Councils + MCTS Planner   |
                     +-----------------------------+
```

---

## The 9 Sovereign Pillars

| Pillar | Package | Command | Core Capability |
| :--- | :--- | :--- | :--- |
| **1. Governance** | `packages/unigov` | `unigov` | Task DAG, Invariant Locking, Drift Reconciler & UniGov 2.0 Organs |
| **2. Skills** | `packages/uniskill` | `uniskill` | Surgical Skill Router & Zero-Noise Token Economizer (88.9% savings) |
| **3. Memory** | `packages/unimemory` | `unimemory` | 5-Tier Living Memory Substrate (`brain_memory.db`) & HippoRAG 2 |
| **4. Verification** | `packages/univerify` | `univerify` | 4-Tier Gatekeeper (Z3 SMT Solver, Law-000 Guard, Touch Bounds) |
| **5. Execution** | `packages/uniexec` | `uniexec` | Linux Bubblewrap (`bwrap`) Sandboxed Code-Mode Micro-Runtime |
| **6. IPC Bus** | `packages/unibus` | `unibus` | Real-Time Unix Domain Socket IPC & File Work Mutex Bus |
| **7. Watchdog** | `packages/uniwatch` | `uniwatch` | Linux Inotify Continuous Sentinel & Balanced AST Watchdog |
| **8. Coding Triad** | `packages/sovereign_triad` | `triad` | Python + Kotlin + Security AppSec Specialist Council |
| **9. Deliberation** | `packages/deliberation` | `deliberate` | Frontal Lobe Deliberative Councils (5) & MCTS Code Planner |

---

## UniGov 2.0: The 5 Autonomous Cognitive Organs

```text
[1. Cartography] ---> [2. Screen Intel] ---> [3. Vision Anchor]
       |                                              |
       v                                              v
[5. Reflex Learner] <--- [4. Auto Red-Team Trigger] <-+
```

1. **`unigov cartography`** (`cartography.py`) — Polyglot stack detection (Android Compose, Next.js 15, Rust, Python) & Clean Architecture layer classification (`DOMAIN`, `DATA`, `PRESENTATION`, `INFRASTRUCTURE`).
2. **`unigov screen-intel`** (`screen_intel.py`) — Compose & TSX spatial layout tree extractor verifying 48x48dp touch targets, system bar insets, and scroll containers.
3. **`unigov vision-eval`** (`vision_anchor.py`) — Offline-first local DB fallback audit, Law ACC-001 integer-paise financial check, and UI readability verification.
4. **`unigov auto-deliberate`** (`auto_deliberation.py`) — Context-aware blast-radius & domain sensitivity risk scorer (`FINANCIAL`, `AUTH`, `SAFETY`, `DATABASE_SCHEMA`) with autonomous Red Team critique triggers.
5. **`unigov learn-reflex`** (`reflexive_learner.py`) — Failure pattern clustering & candidate invariant synthesis queued to `UniEvolve` (`PENDING_APPROVAL`).

---

## Quick Start & Master CLI

```bash
# 1-phrase instant workspace bootstrap (auto-introspects project & activates governance)
uniforge activate

# Run holistic system diagnostics across all pillars
uniforge doctor

# View active workspace governance, constraints & DAG status
uniforge status [path]

# Initialize a new project workspace manually
uniforge init /path/to/project --project-name "MyProject" --objective "Core Objective"

# Run automated test suites across packages
uniforge test [--package unigov]

# Display suite version & manifest
uniforge version
```

---

## Repository Layout

```text
UniForge/
├── bin/                   # Global CLI wrappers & symlinks
├── src/uniforge/          # Master CLI, planner, synthesizer & workspace router
├── packages/
│   ├── unigov/            # Sovereign Governance Engine & 5 Cognitive Organs
│   ├── uniskill/          # Surgical Skill Router & Economizer
│   ├── unimemory/         # 5-Tier Memory & HippoRAG 2 Graph
│   ├── univerify/         # Z3 SMT & Law-000 Gatekeeper
│   ├── uniexec/           # Bubblewrap Sandboxed Execution
│   ├── unibus/            # UDS IPC & Work Mutex Bus
│   ├── uniwatch/          # Inotify AST Sentinel
│   ├── sovereign_triad/   # 3-Specialist Coding Triad
│   └── deliberation/      # 5 Councils + MCTS Planner
├── PLANNING/              # Architectural plans & cognitive brain state
├── pyproject.toml         # Package configuration
└── Makefile               # Build & test targets
```

---

<div align="center">
  <sub>Architected by <strong>Founder Shoeb Ahmad</strong> &amp; <strong>Antigravity (UniAi)</strong></sub>
</div>
