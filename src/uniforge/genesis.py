"""UniForge Genesis: Universal Vision-to-Architecture, UI/UX & Project Skeleton Engine.

Takes any raw project vision/idea and produces:
1. Vision Categorization (domain, platforms, offline/sync needs, core constraints)
2. Tech Stack Recommendation (primary stack, alternatives, rationale)
3. Clean Architecture & ASCII Data-Flow Blueprint
4. UI/UX Direction & Screen Map (with 5 UI states per screen)
5. Phased Strategic Roadmap & UniGov Task DAG registration
6. Runnable Project Skeleton Generator (100% portable, zero hardcoded machine paths)
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()

FIVE_UI_STATES = ("Loading", "Empty", "Error", "Success", "Offline")


# ==============================================================================
# 1. DOMAIN MODELS
# ==============================================================================


class VisionProfile(BaseModel):
    raw_vision: str
    project_name: str
    domain: str
    target_platforms: List[str]
    offline_first: bool
    core_constraints: List[str]
    key_entities: List[str]


class TechStackRecommendation(BaseModel):
    stack_id: str
    primary_stack: Dict[str, str]
    alternatives: List[Dict[str, str]]
    rationale: List[str]


class ArchitectureBlueprint(BaseModel):
    layers: Dict[str, List[str]]
    data_flow_ascii: str
    core_models: List[str]
    contracts: List[str]


class ScreenSpec(BaseModel):
    name: str
    purpose: str
    states: List[str] = Field(default_factory=lambda: list(FIVE_UI_STATES))


class UiUxSuggestion(BaseModel):
    visual_style: str
    color_palette: Dict[str, str]
    typography: str
    screens: List[ScreenSpec]


class RoadmapTask(BaseModel):
    task_id: str
    title: str
    layer: str
    verify_cmd: str


class RoadmapPhase(BaseModel):
    phase_id: str
    title: str
    tasks: List[RoadmapTask]


class GenesisBlueprint(BaseModel):
    vision: VisionProfile
    tech_stack: TechStackRecommendation
    architecture: ArchitectureBlueprint
    ui_ux: UiUxSuggestion
    roadmap: List[RoadmapPhase]


# ==============================================================================
# 2. CLASSIFICATION & STACK TABLES (Uniform Data-Driven Mapping)
# ==============================================================================

DOMAIN_RULES: List[Dict[str, Any]] = [
    {
        "domain": "RETAIL_POS",
        "keywords": ("pos", "billing", "shop", "store", "showroom", "inventory", "stock", "invoice", "khata", "dukaan", "retail", "imei"),
        "entities": ["Product", "InventoryUnit", "Invoice", "Customer", "LedgerEntry", "Supplier"],
        "constraints": [
            "Offline-first local SQLite persistence with zero internet dependency for billing",
            "Integer-paise / fixed-point math for all money & tax calculations (zero floating-point drift)",
            "Fast checkout flow (<3s barcode/item scan to invoice)",
        ],
    },
    {
        "domain": "HEALTHCARE",
        "keywords": ("clinic", "hospital", "pharmacy", "medicine", "patient", "doctor", "emr", "fhir", "health", "medical"),
        "entities": ["Patient", "Prescription", "InventoryBatch", "Invoice", "Appointment"],
        "constraints": [
            "Batch & expiry tracking with strict FEFO (First-Expired-First-Out) validation",
            "Patient data encryption at rest and role-based access control",
            "Offline resilience for clinic/counter operations",
        ],
    },
    {
        "domain": "FINTECH",
        "keywords": ("finance", "accounting", "ledger", "bank", "payment", "upi", "wallet", "trading", "expense", "tax", "gst"),
        "entities": ["Account", "JournalEntry", "Transaction", "AuditLog", "ReconciliationBatch"],
        "constraints": [
            "Double-entry bookkeeping invariant: sum(debits) == sum(credits)",
            "Strict integer-minor-unit arithmetic (zero IEEE-754 float in financial math)",
            "Immutable append-only audit trail for every mutation",
        ],
    },
    {
        "domain": "AI_SYSTEM",
        "keywords": ("ai", "agent", "llm", "rag", "ml", "model", "neural", "inference", "vector", "memory", "chatbot"),
        "entities": ["AgentTask", "MemoryNode", "EmbeddingRecord", "ToolCall", "EvaluationRun"],
        "constraints": [
            "Deterministic schema validation on tool outputs",
            "Sandboxed execution for generated code/tools",
            "Token-budget and latency telemetry tracking",
        ],
    },
    {
        "domain": "CLI_DEVTOOL",
        "keywords": ("cli", "terminal", "developer", "sdk", "linter", "compiler", "automation", "script", "devops"),
        "entities": ["WorkspaceConfig", "ExecutionPlan", "TaskNode", "DiagnosticReport"],
        "constraints": [
            "Zero hardcoded machine paths (100% portable across environments)",
            "Clean exit codes, structured JSON output mode, and fast startup",
            "Comprehensive automated unit/integration test coverage",
        ],
    },
    {
        "domain": "SAAS_WEB",
        "keywords": ("saas", "dashboard", "portal", "web", "crm", "erp", "admin", "analytics", "booking", "ecommerce"),
        "entities": ["Tenant", "User", "Workspace", "Record", "AuditEvent"],
        "constraints": [
            "Multi-tenant isolation and strict server-side auth/RBAC checks",
            "Responsive UI across mobile, tablet, and desktop viewports",
            "Typed API contracts shared between backend and frontend",
        ],
    },
]

STACK_CATALOG: Dict[str, Dict[str, Any]] = {
    "android_compose_room": {
        "primary_stack": {
            "Language": "Kotlin 2.x",
            "UI Framework": "Jetpack Compose (Material 3)",
            "Local Database": "Room + SQLite (WAL Mode)",
            "Architecture": "Clean Architecture + MVI / StateFlow",
            "DI & Async": "Hilt + Kotlin Coroutines",
            "Testing": "JUnit4 + Robolectric + Compose UI Test",
        },
        "alternatives": [
            {"Option": "Kotlin Multiplatform (KMP)", "When": "If iOS + Android code sharing is needed from Day 1"},
            {"Option": "Flutter + Drift", "When": "If cross-platform single UI codebase is prioritized over native Android APIs"},
        ],
        "rationale": [
            "Native Jetpack Compose gives 60-120fps counter responsiveness and direct CameraX/Bluetooth hardware access.",
            "Room + SQLite WAL ensures 100% offline-first ACID transactions even with zero network.",
        ],
    },
    "nextjs_postgres": {
        "primary_stack": {
            "Frontend": "Next.js 15 (App Router) + React 19 + TypeScript",
            "Styling": "Tailwind CSS v4 + Radix UI / shadcn",
            "Backend / API": "Next.js Server Actions / Route Handlers + Zod",
            "Database": "PostgreSQL + Drizzle ORM (or Prisma)",
            "Auth": "Auth.js / Supabase Auth with RBAC",
            "Testing": "Vitest + Playwright E2E",
        },
        "alternatives": [
            {"Option": "FastAPI + React (Vite)", "When": "If heavy Python data/AI processing is needed on backend"},
        ],
        "rationale": [
            "End-to-end TypeScript + Zod contracts eliminate frontend/backend schema drift.",
            "Server Components reduce client bundle size and accelerate initial dashboard load.",
        ],
    },
    "python_fastapi": {
        "primary_stack": {
            "Language": "Python 3.12+",
            "API Framework": "FastAPI + Pydantic v2",
            "Storage / Vector": "SQLite / PostgreSQL + LanceDB / Qdrant",
            "Async Runtime": "asyncio TaskGroups + uv",
            "Testing": "pytest + httpx TestClient",
        },
        "alternatives": [
            {"Option": "Go + Fiber", "When": "If ultra-low-latency high-concurrency microservices are primary"},
        ],
        "rationale": [
            "First-class ecosystem for AI/ML, embeddings, Z3 verification, and rapid API iteration.",
            "Pydantic v2 enforces strict runtime validation on all inputs and agent outputs.",
        ],
    },
    "python_cli": {
        "primary_stack": {
            "Language": "Python 3.11+",
            "CLI Framework": "Typer + Rich",
            "Data Validation": "Pydantic v2",
            "Local State": "SQLite (WAL) / JSON",
            "Testing": "pytest",
        },
        "alternatives": [
            {"Option": "Rust (clap + ratatui)", "When": "If single static binary and sub-5ms cold start are critical"},
        ],
        "rationale": [
            "Typer + Rich delivers clean help menus, tables, trees, and JSON output with minimal boilerplate.",
            "Cross-platform packaging via pyproject.toml works cleanly on Linux, macOS, and Windows.",
        ],
    },
    "rust_desktop": {
        "primary_stack": {
            "Language": "Rust (2021/2024 Edition)",
            "Windowing & GPU": "winit + wgpu",
            "Text & Layout": "glyphon / cosmic-text",
            "Testing": "cargo test + integration harness",
        },
        "alternatives": [
            {"Option": "Tauri (Rust + Web UI)", "When": "If rapid HTML/CSS UI iteration is preferred over custom GPU rendering"},
        ],
        "rationale": [
            "Zero garbage-collector pauses and native OS windowing with minimal memory footprint.",
        ],
    },
}


# ==============================================================================
# 3. VISION GENESIS ARCHITECT
# ==============================================================================


class VisionGenesisArchitect:
    """Transforms any raw project vision into a categorized, architected, scaffoldable plan."""

    def _derive_project_name(self, vision: str, explicit_name: Optional[str]) -> str:
        if explicit_name and explicit_name.strip():
            return explicit_name.strip()
        words = [w for w in re.findall(r"[A-Za-z0-9]+", vision) if len(w) > 2]
        stop = {"app", "for", "and", "the", "with", "banana", "hai", "chahiye", "ek", "for", "system", "tool"}
        picked = [w.capitalize() for w in words if w.lower() not in stop][:3]
        return "".join(picked) if picked else "UniProject"

    def categorize_vision(self, vision: str, project_name: Optional[str] = None) -> VisionProfile:
        """Step 1: Categorize domain, target platforms, offline needs, and constraints."""
        lower = vision.lower()
        matched_rule = None
        best_hits = 0
        for rule in DOMAIN_RULES:
            hits = sum(1 for kw in rule["keywords"] if kw in lower)
            if hits > best_hits:
                best_hits = hits
                matched_rule = rule

        domain = matched_rule["domain"] if matched_rule else "GENERAL_APP"
        entities = list(matched_rule["entities"]) if matched_rule else ["User", "Workspace", "Item", "ActivityLog"]
        constraints = list(matched_rule["constraints"]) if matched_rule else [
            "Clean Architecture boundary separation (Domain isolated from UI/DB)",
            "Automated unit and integration tests for all core workflows",
        ]

        platforms: List[str] = []
        if any(re.search(rf"\b{k}\b", lower) for k in ("android", "mobile", "phone", "app", "apk", "pos", "showroom")):
            platforms.append("Android")
        if any(re.search(rf"\b{k}\b", lower) for k in ("web", "saas", "portal", "dashboard", "browser", "website", "next")):
            platforms.append("Web")
        if any(re.search(rf"\b{k}\b", lower) for k in ("cli", "terminal", "command", "tool")):
            platforms.append("CLI")
        if any(re.search(rf"\b{k}\b", lower) for k in ("desktop", "linux", "windows", "macos", "native")):
            platforms.append("Desktop")
        if any(re.search(rf"\b{k}\b", lower) for k in ("api", "backend", "server", "ai", "agent")):
            platforms.append("Backend/API")
        if not platforms:
            platforms = ["Web"] if domain == "SAAS_WEB" else ["Python"]

        offline_first = any(
            k in lower for k in ("offline", "local", "sqlite", "pos", "dukaan", "showroom", "cli", "desktop")
        ) or domain in ("RETAIL_POS", "HEALTHCARE")

        return VisionProfile(
            raw_vision=vision.strip(),
            project_name=self._derive_project_name(vision, project_name),
            domain=domain,
            target_platforms=platforms,
            offline_first=offline_first,
            core_constraints=constraints,
            key_entities=entities,
        )

    def recommend_tech_stack(self, profile: VisionProfile) -> TechStackRecommendation:
        """Step 2: Select optimal stack based on categorized domain and platforms."""
        if "Android" in profile.target_platforms:
            stack_id = "android_compose_room"
        elif "Desktop" in profile.target_platforms and profile.domain == "CLI_DEVTOOL":
            stack_id = "rust_desktop"
        elif "CLI" in profile.target_platforms or (
            profile.domain == "CLI_DEVTOOL" and "Web" not in profile.target_platforms
        ):
            stack_id = "python_cli"
        elif profile.domain == "AI_SYSTEM" or (
            "Backend/API" in profile.target_platforms and "Web" not in profile.target_platforms
        ):
            stack_id = "python_fastapi"
        elif "Web" in profile.target_platforms or profile.domain in ("SAAS_WEB", "FINTECH"):
            stack_id = "nextjs_postgres"
        else:
            stack_id = "python_fastapi"

        entry = STACK_CATALOG[stack_id]
        return TechStackRecommendation(
            stack_id=stack_id,
            primary_stack=dict(entry["primary_stack"]),
            alternatives=list(entry["alternatives"]),
            rationale=list(entry["rationale"]),
        )

    def design_architecture(
        self, profile: VisionProfile, stack: TechStackRecommendation
    ) -> ArchitectureBlueprint:
        """Step 3: Design Clean Architecture layers, ASCII data-flow, and contracts."""
        layers = {
            "domain": [f"{e}Model" for e in profile.key_entities] + ["ValidationInvariants"],
            "data": [f"{e}Repository" for e in profile.key_entities[:3]] + [
                "LocalDatabase" if profile.offline_first else "ApiClient"
            ],
            "presentation": ["AppNavigation", "StateViewModel", "ThemeTokens", "ReusableComponents"],
            "infrastructure": ["ConfigLoader", "DependencyInjection", "TestHarness"],
        }

        storage_label = "Local SQLite (WAL) + Sync" if profile.offline_first else "PostgreSQL / API Store"
        data_flow_ascii = (
            "+-------------------+     Intent      +---------------------------+\n"
            "|  UI / Presentation| --------------> |     Domain / UseCases     |\n"
            "| (Screens & States)| <-------------- |     (Pure Invariants)     |\n"
            "+-------------------+   StateFlow     +---------------------------+\n"
            "                                                    |\n"
            "                                                    v\n"
            "                                      +---------------------------+\n"
            "                                      |      Data Repository      |\n"
            f"                                      | {storage_label:<25} |\n"
            "                                      +---------------------------+"
        )

        contracts = [
            f"{e}Repository.save(item: {e}) -> Result" for e in profile.key_entities[:3]
        ]
        return ArchitectureBlueprint(
            layers=layers,
            data_flow_ascii=data_flow_ascii,
            core_models=list(profile.key_entities),
            contracts=contracts,
        )

    def suggest_ui_ux(
        self, profile: VisionProfile, stack: TechStackRecommendation
    ) -> UiUxSuggestion:
        """Step 4: Recommend visual direction, palette, typography, and screen specs."""
        if stack.stack_id == "python_cli":
            return UiUxSuggestion(
                visual_style="High-Contrast Terminal UI (Rich Panels, Tables & Trees)",
                color_palette={"Primary": "Cyan", "Success": "Emerald Green", "Warning": "Amber", "Error": "Red"},
                typography="Monospace Terminal Font (JetBrains Mono / Fira Code)",
                screens=[
                    ScreenSpec(name="CLI Status Dashboard", purpose="Show workspace health, constraints, and active tasks"),
                    ScreenSpec(name="Interactive Wizard", purpose="Collect user inputs with validation & clear feedback"),
                ],
            )

        if profile.domain in ("RETAIL_POS", "HEALTHCARE"):
            style = "Tactile Soft-Surface POS (High Contrast, 48dp+ Touch Targets, Zero Clutter)"
            palette = {
                "Primary": "#0F766E (Teal Emerald)",
                "Accent": "#2563EB (Electric Blue)",
                "Background": "#F8FAFC (Warm Off-White)",
                "Error": "#DC2626 (Crisp Red)",
            }
            screens = [
                ScreenSpec(name="Home Dashboard", purpose="Daily summary, quick actions & alerts"),
                ScreenSpec(name="Primary Operations / Billing", purpose="Fast scan/search, cart & checkout"),
                ScreenSpec(name="Inventory / Stock In", purpose="Catalog selection, batch/serial inward & review"),
                ScreenSpec(name="Records & Ledger", purpose="Searchable history, dues & statements"),
                ScreenSpec(name="Settings & Sync", purpose="Profile, hardware & backup controls"),
            ]
        else:
            style = "Clean Minimalist Workspace (Linear/Stripe Clarity, Card Hierarchy)"
            palette = {
                "Primary": "#2563EB (Royal Blue)",
                "Accent": "#10B981 (Emerald)",
                "Background": "#F9FAFB (Neutral Canvas)",
                "Error": "#EF4444 (Rose Red)",
            }
            screens = [
                ScreenSpec(name="Overview Dashboard", purpose="Key metrics, status & primary CTA"),
                ScreenSpec(name="Core Workspace View", purpose=f"Manage {', '.join(profile.key_entities[:2])}"),
                ScreenSpec(name="Detail & Edit Inspector", purpose="View/update item details with validation"),
                ScreenSpec(name="Settings & Access", purpose="Configuration, roles & preferences"),
            ]

        return UiUxSuggestion(
            visual_style=style,
            color_palette=palette,
            typography="Inter / Plus Jakarta Sans (Tabular numerals for prices & counts)",
            screens=screens,
        )

    def build_roadmap(
        self,
        profile: VisionProfile,
        stack: TechStackRecommendation,
        arch: ArchitectureBlueprint,
        ui: UiUxSuggestion,
    ) -> List[RoadmapPhase]:
        """Step 5: Build a 3-phase topological implementation roadmap."""
        test_cmd = {
            "android_compose_room": "./gradlew testDebugUnitTest",
            "nextjs_postgres": "npm test",
            "python_fastapi": "pytest -q",
            "python_cli": "pytest -q",
            "rust_desktop": "cargo test",
        }.get(stack.stack_id, "pytest -q")

        return [
            RoadmapPhase(
                phase_id="PHASE-1",
                title="Foundation, Domain Models & Storage",
                tasks=[
                    RoadmapTask(
                        task_id="T1-1",
                        title=f"Initialize {stack.stack_id} project structure & CI test harness",
                        layer="INFRASTRUCTURE",
                        verify_cmd=test_cmd,
                    ),
                    RoadmapTask(
                        task_id="T1-2",
                        title=f"Implement domain models ({', '.join(arch.core_models[:4])}) & invariants",
                        layer="DOMAIN",
                        verify_cmd=test_cmd,
                    ),
                    RoadmapTask(
                        task_id="T1-3",
                        title="Implement repository & persistence layer",
                        layer="DATA",
                        verify_cmd=test_cmd,
                    ),
                ],
            ),
            RoadmapPhase(
                phase_id="PHASE-2",
                title="Core Workflows & UI Screens",
                tasks=[
                    RoadmapTask(
                        task_id="T2-1",
                        title=f"Build primary screens ({', '.join(s.name for s in ui.screens[:3])}) with 5 UI states",
                        layer="PRESENTATION",
                        verify_cmd=test_cmd,
                    ),
                    RoadmapTask(
                        task_id="T2-2",
                        title="Wire end-to-end validation, error handling & offline resilience",
                        layer="PRESENTATION",
                        verify_cmd=test_cmd,
                    ),
                ],
            ),
            RoadmapPhase(
                phase_id="PHASE-3",
                title="Verification, Security & Release",
                tasks=[
                    RoadmapTask(
                        task_id="T3-1",
                        title="Run full regression suite, static lints & edge-case tests",
                        layer="TEST",
                        verify_cmd=test_cmd,
                    ),
                ],
            ),
        ]

    def generate_blueprint(self, vision: str, project_name: Optional[str] = None) -> GenesisBlueprint:
        profile = self.categorize_vision(vision, project_name)
        stack = self.recommend_tech_stack(profile)
        arch = self.design_architecture(profile, stack)
        ui = self.suggest_ui_ux(profile, stack)
        roadmap = self.build_roadmap(profile, stack, arch, ui)
        return GenesisBlueprint(
            vision=profile,
            tech_stack=stack,
            architecture=arch,
            ui_ux=ui,
            roadmap=roadmap,
        )

    def export_blueprint_markdown(self, bp: GenesisBlueprint, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines: List[str] = [
            f"# {bp.vision.project_name} — Master Architecture Blueprint",
            "",
            f"> **Vision:** {bp.vision.raw_vision}",
            "",
            "## 1. Vision Categorization",
            f"- **Domain:** `{bp.vision.domain}`",
            f"- **Target Platforms:** {', '.join(bp.vision.target_platforms)}",
            f"- **Offline-First:** {'Yes' if bp.vision.offline_first else 'No'}",
            f"- **Core Entities:** {', '.join(bp.vision.key_entities)}",
            "- **Locked Constraints:**",
        ]
        lines.extend(f"  - {c}" for c in bp.vision.core_constraints)
        lines.extend(["", "## 2. Recommended Tech Stack", f"- **Stack Profile:** `{bp.tech_stack.stack_id}`"])
        for k, v in bp.tech_stack.primary_stack.items():
            lines.append(f"  - **{k}:** {v}")
        lines.append("- **Why this stack:**")
        lines.extend(f"  - {r}" for r in bp.tech_stack.rationale)
        if bp.tech_stack.alternatives:
            lines.append("- **Alternatives:**")
            for alt in bp.tech_stack.alternatives:
                lines.append(f"  - **{alt['Option']}:** {alt['When']}")

        lines.extend([
            "",
            "## 3. Clean Architecture & Data Flow",
            "```text",
            bp.architecture.data_flow_ascii,
            "```",
            "",
            "### Layers",
        ])
        for layer, items in bp.architecture.layers.items():
            lines.append(f"- **{layer.upper()}:** {', '.join(items)}")

        lines.extend([
            "",
            "## 4. UI/UX Direction & Screen Map",
            f"- **Visual Style:** {bp.ui_ux.visual_style}",
            f"- **Typography:** {bp.ui_ux.typography}",
            "- **Color Palette:**",
        ])
        for k, v in bp.ui_ux.color_palette.items():
            lines.append(f"  - **{k}:** `{v}`")
        lines.append("- **Screens (All 5 UI States: Loading / Empty / Error / Success / Offline):**")
        for s in bp.ui_ux.screens:
            lines.append(f"  - **{s.name}:** {s.purpose}")

        lines.extend(["", "## 5. Implementation Roadmap"])
        for phase in bp.roadmap:
            lines.append(f"### {phase.phase_id}: {phase.title}")
            for t in phase.tasks:
                lines.append(f"- [ ] `{t.task_id}` [{t.layer}] {t.title} (`{t.verify_cmd}`)")

        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return out_path

    def register_unigov_tasks(self, bp: GenesisBlueprint, target_dir: Path) -> int:
        """Initialize .unigov/state.db if absent and register roadmap tasks cleanly."""
        gov_dir = target_dir / ".unigov"
        gov_dir.mkdir(parents=True, exist_ok=True)
        db_path = gov_dir / "state.db"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        conn = sqlite3.connect(str(db_path))
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS project_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    parent_id TEXT,
                    level TEXT,
                    title TEXT,
                    description TEXT,
                    status TEXT,
                    verify_cmd TEXT,
                    created_at TEXT
                );
                """
            )
            conn.execute(
                "INSERT OR REPLACE INTO project_meta (key, value) VALUES (?, ?)",
                ("project_name", bp.vision.project_name),
            )
            conn.execute(
                "INSERT OR REPLACE INTO project_meta (key, value) VALUES (?, ?)",
                ("objective", bp.vision.raw_vision),
            )
            conn.execute(
                "INSERT OR REPLACE INTO project_meta (key, value) VALUES (?, ?)",
                ("domain", bp.vision.domain),
            )

            count = 0
            for phase in bp.roadmap:
                for idx, t in enumerate(phase.tasks):
                    status = "READY" if (phase.phase_id == "PHASE-1" and idx == 0) else "PENDING"
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO tasks
                        (id, parent_id, level, title, description, status, verify_cmd, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (t.task_id, phase.phase_id, "TASK", t.title, f"Layer: {t.layer}", status, t.verify_cmd, now),
                    )
                    count += 1
            conn.commit()
            return count
        finally:
            conn.close()

    def scaffold_skeleton(
        self, bp: GenesisBlueprint, target_dir: Path, force: bool = False
    ) -> List[str]:
        """Step 6: Create portable, runnable starter folder structure for the recommended stack."""
        created: List[str] = []
        slug = re.sub(r"[^a-z0-9_]+", "_", bp.vision.project_name.lower()).strip("_") or "app"
        stack_id = bp.tech_stack.stack_id

        def write_if_allowed(rel_path: str, content: str) -> None:
            dest = target_dir / rel_path
            if dest.exists() and not force:
                return
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            created.append(rel_path)

        # Common docs
        write_if_allowed(
            "README.md",
            f"# {bp.vision.project_name}\n\n{bp.vision.raw_vision}\n\n"
            f"- **Domain:** `{bp.vision.domain}`\n"
            f"- **Stack:** `{stack_id}`\n"
            f"- **Blueprint:** `PLANNING/MASTER_ARCHITECTURE_BLUEPRINT.md`\n",
        )

        if stack_id in ("python_cli", "python_fastapi"):
            is_api = stack_id == "python_fastapi"
            deps = '["fastapi>=0.115.0", "pydantic>=2.0.0", "uvicorn>=0.30.0"]' if is_api else '["typer>=0.9.0", "rich>=13.0.0", "pydantic>=2.0.0"]'
            write_if_allowed(
                "pyproject.toml",
                f'[build-system]\nrequires = ["setuptools>=61.0"]\nbuild-backend = "setuptools.build_meta"\n\n'
                f'[project]\nname = "{slug}"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
                f'dependencies = {deps}\n\n[tool.setuptools.packages.find]\nwhere = ["src"]\n',
            )
            write_if_allowed(f"src/{slug}/__init__.py", f'"""{bp.vision.project_name} package."""\n')
            write_if_allowed(
                f"src/{slug}/domain/models.py",
                "from pydantic import BaseModel\n\n\n"
                + "\n\n".join(
                    f"class {e}(BaseModel):\n    id: str\n    name: str\n"
                    for e in bp.vision.key_entities
                ),
            )
            write_if_allowed(f"src/{slug}/data/__init__.py", "")
            write_if_allowed(
                f"src/{slug}/main.py",
                'def health() -> dict[str, str]:\n    return {"status": "ok"}\n',
            )
            write_if_allowed(
                "tests/test_smoke.py",
                f"from {slug}.main import health\n\n\ndef test_health() -> None:\n    assert health()['status'] == 'ok'\n",
            )
        elif stack_id == "nextjs_postgres":
            write_if_allowed(
                "package.json",
                json.dumps(
                    {
                        "name": slug.replace("_", "-"),
                        "version": "0.1.0",
                        "private": True,
                        "scripts": {"dev": "next dev", "build": "next build", "test": "vitest run"},
                    },
                    indent=2,
                )
                + "\n",
            )
            write_if_allowed(
                "src/domain/models.ts",
                "\n".join(f"export interface {e} {{\n  id: string;\n  name: string;\n}}\n" for e in bp.vision.key_entities),
            )
            write_if_allowed("src/data/repository.ts", "// Repository interfaces & persistence adapters\n")
            write_if_allowed(
                "src/app/page.tsx",
                f"export default function HomePage() {{\n  return <main><h1>{bp.vision.project_name}</h1></main>;\n}}\n",
            )
        elif stack_id == "android_compose_room":
            pkg_path = f"app/src/main/java/com/app/{slug}"
            write_if_allowed(
                f"{pkg_path}/domain/Models.kt",
                f"package com.app.{slug}.domain\n\n"
                + "\n".join(f"data class {e}(val id: String, val name: String)" for e in bp.vision.key_entities)
                + "\n",
            )
            write_if_allowed(
                f"{pkg_path}/data/Repository.kt",
                f"package com.app.{slug}.data\n\n// Room DAO & offline-first repository contracts\n",
            )
            write_if_allowed(
                f"{pkg_path}/ui/MainScreen.kt",
                f"package com.app.{slug}.ui\n\n// Jetpack Compose Material 3 entry screen\n",
            )
            write_if_allowed(
                f"app/src/test/java/com/app/{slug}/SmokeTest.kt",
                f"package com.app.{slug}\n\nimport org.junit.Assert.assertTrue\nimport org.junit.Test\n\n"
                "class SmokeTest {\n    @Test fun sanity() { assertTrue(true) }\n}\n",
            )
        else:
            write_if_allowed(
                "Cargo.toml",
                f'[package]\nname = "{slug}"\nversion = "0.1.0"\nedition = "2021"\n',
            )
            write_if_allowed("src/main.rs", f'fn main() {{\n    println!("{bp.vision.project_name} initialized");\n}}\n')

        return created

    def render_terminal_report(self, bp: GenesisBlueprint) -> None:
        """Render rich terminal summary of the generated blueprint."""
        console.print(
            Panel.fit(
                f"[bold cyan]{bp.vision.project_name}[/bold cyan]  [dim]|  Domain:[/dim] [bold yellow]{bp.vision.domain}[/bold yellow]\n"
                f"[white]Platforms:[/white] {', '.join(bp.vision.target_platforms)}  |  "
                f"[white]Offline-First:[/white] {'Yes' if bp.vision.offline_first else 'No'}\n"
                f"[dim]Entities:[/dim] {', '.join(bp.vision.key_entities)}",
                title="1. Vision Categorization",
                border_style="cyan",
            )
        )

        stack_table = Table(title=f"2. Recommended Tech Stack ({bp.tech_stack.stack_id})")
        stack_table.add_column("Layer", style="cyan", no_wrap=True)
        stack_table.add_column("Choice", style="green")
        for k, v in bp.tech_stack.primary_stack.items():
            stack_table.add_row(k, v)
        console.print(stack_table)

        console.print(Panel(bp.architecture.data_flow_ascii, title="3. Architecture Data Flow", border_style="blue"))

        ui_tree = Tree(f"[bold magenta]4. UI/UX: {bp.ui_ux.visual_style}[/bold magenta]")
        for s in bp.ui_ux.screens:
            ui_tree.add(f"[bold]{s.name}[/bold] — {s.purpose} [dim](5 states)[/dim]")
        console.print(ui_tree)

        road_tree = Tree("[bold green]5. Strategic Roadmap[/bold green]")
        for phase in bp.roadmap:
            p_branch = road_tree.add(f"[bold cyan]{phase.phase_id}: {phase.title}[/bold cyan]")
            for t in phase.tasks:
                p_branch.add(f"[{t.layer}] {t.task_id}: {t.title}")
        console.print(road_tree)
