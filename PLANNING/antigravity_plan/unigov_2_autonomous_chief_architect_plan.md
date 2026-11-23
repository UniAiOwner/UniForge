# UniGov 2.0: The Autonomous Sovereign Chief Architect Implementation Plan

## 1. Overview & Objective
Transform UniGov from a passive reactive task/invariant runner into an active **Autonomous Chief Architect Cognitive Brain**.
UniGov 2.0 autonomously:
1. Discovers and deeply maps any project's architecture, dependencies, and Clean Architecture layers.
2. Parses screens, Composables, and TSX visual components into a spatial layout tree, verifying touch targets and insets.
3. Evaluates all proposals against Founder Shoeb Ahmad's Vision (Bidhuna showroom offline-first reality, Law ACC-001 integer paise, 2.5D tactile elegance).
4. Auto-triggers Red Team and Devil's Advocate whenever blast radius or domain risk crosses thresholds without needing manual user prompts.
5. Clusters episodic failure patterns to autonomously synthesize new invariant rules via UniEvolve (2-Phase Commit).

Strict Constraint: All development, testing, and verification will occur strictly inside UniForge and its package test suites with synthetic fixtures. No external projects will be mutated or tested during this phase.

---

## 2. The 5 Cognitive Organs

### Organ 1: Universal Codebase & Architecture Cartography (`unigov/cartography.py`)
- **Polyglot Stack Detection**: Identifies stack type (Android Compose, Web Next.js 15, Rust Systems, Python Service).
- **Clean Architecture Layering**: Automatically classifies files into:
  - `DOMAIN`: Entities, Value Objects, UseCases, Domain Invariants.
  - `DATA`: Repositories, Database DAOs, Network DTOs, Mappers.
  - `PRESENTATION`: ViewModels, StateHolders, Screens, Components.
  - `INFRASTRUCTURE`: Config, Build toolchains, DI modules.
- **Symbol Call & Blast Radius Graph**: Dependency mapping of classes and functions.

### Organ 2: Screen & Spatial Layout Intelligence (`unigov/screen_intel.py`)
- **Compose & TSX UI AST Extraction**:
  - Detects screen entry points (`@Composable fun *Screen*`, Next.js `page.tsx`).
  - Extracts visual hierarchy: Scaffolds, TopBars, BottomBars, NavigationRails, Card items, Floating Action Buttons, Dialogs.
  - Inspects layout constraints: Touch target bounds (48x48dp), insets padding (`systemBarsPadding`, `imePadding`), scroll containers.

### Organ 3: Founder Vision & Ground Reality Anchor (`unigov/vision_anchor.py`)
- **Vision Invariant Evaluator**:
  - Showroom Offline-First Invariant: Verifies local database fallback for network calls.
  - Law ACC-001 Zero-Float Financial Invariant: Flags any floating-point money or tax types.
  - Aesthetic & Tactile Invariant: Checks for loading shimmers, haptic feedback hooks, high-contrast readable typography.

### Organ 4: Autonomous Deliberative Reflex & Red Team Auto-Trigger (`unigov/auto_deliberation.py`)
- **Context-Aware Risk Scorer**:
  - Computes blast radius score: file count, caller depth, domain sensitivity (`FINANCIAL`, `AUTH`, `SAFETY`, `DATABASE_SCHEMA`).
- **Autonomous Devil's Advocate / Red Team Summoner**:
  - Automatically executes adversarial critique if risk score >= threshold.
  - Generates concrete counter-arguments, race-condition warnings, and edge-case attacks.

### Organ 5: Episodic Learning & Reflexive Rule Synthesizer (`unigov/reflexive_learner.py`)
- **Law-STARK Failure Mining**:
  - Clusters recurring compiler, test, or delimiter errors from execution traces.
  - Generates candidate invariant rules or linter checks.
  - Submits candidate rules to `UniEvolve` as `PENDING_APPROVAL` (Lock 3 protected).

---

## 3. Implementation Steps
1. Create `unigov/cartography.py` + unit tests.
2. Create `unigov/screen_intel.py` + unit tests.
3. Create `unigov/vision_anchor.py` + unit tests.
4. Create `unigov/auto_deliberation.py` + unit tests.
5. Create `unigov/reflexive_learner.py` + unit tests.
6. Wire CLI commands into `unigov/cli.py` (`unigov cartography`, `unigov screen-intel`, `unigov vision-eval`, `unigov auto-deliberate`, `unigov learn-reflex`).
7. Run complete 9-package test suite (`uniforge test`) and `uniforge doctor`.
8. Log achievements in `UniForge/dev_logs.txt`.
