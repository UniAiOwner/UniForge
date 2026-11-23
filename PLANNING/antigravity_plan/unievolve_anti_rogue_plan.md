# UniEvolve: Anti-Rogue Self-Improvement Subsystem Blueprint

## 1. Overview
UniEvolve is the sovereign continuous self-improvement and optimization engine of UniForge. It enables autonomous performance profiling, dead code removal, algorithm optimization, and invariant tightening while strictly preventing "Reward Hacking" or rogue behaviors through 3 non-negotiable security locks.

## 2. The 3 Security Hard-Locks (Anti-Rogue Foundation)

```
Candidate Optimization
         │
         ▼
[Lock 1: Canonical Path & AST Sentinel]
  ├── Path.resolve() check against Immutable Files
  │     (tests/, evolution.py, z3_prover, invariants, db.py)
  └── AST Walk: Blocks exec(), eval(), ctypes, __import__, @pytest.mark.skip
         │ PASS
         ▼
[Lock 2: Double-Sandboxed Shadow Evaluation]
  ├── Isolated Bubblewrap (bwrap) execution
  └── Strict --ro-bind on tests/ and constitutional safety gates
         │ PASS
         ▼
[Lock 3: Monotonic Regression Gate & 2-Phase Commit]
  ├── Zero-Regression Invariant: Test count & pass rate must NOT decrease
  ├── Benchmark Improvement: Candidate must strictly beat baseline
  └── 2-Phase Commit: Proposal saved as PENDING_APPROVAL
         │
         ▼
[Founder Sovereign Ratification Gate]
  └── unigov evolution-approve <id> required before live codebase touches!
```

### Lock 1: Immutable Kernel & Test Armor
- **Immutable Target Set**:
  - `tests/**` (all test suites and assertions)
  - `*evolution*` (the self-improvement engine itself)
  - `*z3*` and `*prover*` (mathematical verification solver)
  - `*invariants*` and `*gatekeeper*` (constitutional guards)
  - `*db.py` and state database definitions
- **Resolution**: All path checks enforce `Path.resolve()` to prevent symlink and relative directory traversal (`../`).
- **AST Forbidden Calls**: `eval`, `exec`, `__import__`, `importlib`, `ctypes`, `subprocess`, `@pytest.mark.skip`, `@pytest.mark.xfail`.

### Lock 2: Sandboxed Shadow Evaluation
- Runs entirely inside a shadow copy in an isolated environment.
- Safety files and tests are mounted read-only (`--ro-bind`).

### Lock 3: 2-Phase Commit & Monotonic Invariant
- Candidate status starts at `PROPOSED`.
- After shadow sandbox verification, status transitions to `PENDING_APPROVAL`.
- **Zero Live Code Mutation**: Live files remain 100% untouched during `unigov evolve`.
- Live application requires explicit `unigov evolution-approve <id>`.
- Provides 1-click rollback: `unigov evolution-rollback <id>`.

## 3. Data Schema & Models
- `EvolutionProposal`:
  - `proposal_id`: UUIDv4
  - `target_metric`: `LATENCY`, `TOKEN_ECONOMY`, `DEAD_CODE`, `CODE_COMPACTNESS`
  - `target_file`: Relative file path
  - `original_sha256`: Hash before change
  - `candidate_sha256`: Hash of proposed change
  - `diff_content`: Unified diff text
  - `baseline_metrics`: Benchmark numbers before
  - `candidate_metrics`: Benchmark numbers after
  - `status`: `PENDING_APPROVAL`, `APPROVED`, `APPLIED`, `REJECTED`, `ROLLED_BACK`
  - `created_at`, `approved_at`, `rollback_at`

## 4. Verification Plan
- Unit tests covering:
  1. AntiRogueSentinel blocking edits to `tests/` and safety files.
  2. AST sentinel blocking dynamic code execution (`eval`, `exec`, `__import__`).
  3. Monotonic gate rejecting candidates that fail tests or reduce test counts.
  4. 2-Phase commit ensuring live codebase remains unchanged until approved.
  5. Evolution approval and rollback restoring exact SHA-256 byte-parity.
