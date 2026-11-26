"""UniForge Planner: Sovereign Architectural Roadmap & Task DAG Synthesis Engine.
Pillar 11 of UniForge.
Synthesizes the World-Class 5-Tier Active-Inference Neuro-Symbolic Agent Operating System (AN-AIOS).
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()

class TaskDefinition:
    def __init__(
        self,
        task_id: str,
        parent_id: Optional[str],
        level: str,  # MILESTONE, MODULE, TASK
        layer: str,
        title: str,
        description: str,
        target_files: List[str],
        verify_cmd: str,
        depends_on: List[str],
        invariants: List[str]
    ):
        self.task_id = task_id
        self.parent_id = parent_id
        self.level = level
        self.layer = layer
        self.title = title
        self.description = description
        self.target_files = target_files
        self.verify_cmd = verify_cmd
        self.depends_on = depends_on
        self.invariants = invariants


class SovereignRoadmapPlanner:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.gov_dir = self.workspace_root / ".unigov"
        self.db_path = self.gov_dir / "state.db"

    def synthesize_master_plan(self) -> List[TaskDefinition]:
        """Synthesize the World-Class 5-Tier AN-AIOS Master Roadmap."""
        tasks: List[TaskDefinition] = []

        # =========================================================================
        # PHASE 1: COGNITIVE KERNEL & SYNAPTIC EVENT SCHEDULER
        # =========================================================================
        m1_id = "M1-KERNEL-SCHEDULER"
        tasks.append(TaskDefinition(
            task_id=m1_id,
            parent_id=None,
            level="MILESTONE",
            layer="LAYER_2_SYSTEMS",
            title="Phase 1: Cognitive Kernel & Synaptic Event Process Scheduler",
            description="Build the AIOS-grade preemptive process scheduler, unified signal bus, and zero-copy context manager bridging all agent modules.",
            target_files=["uni_life/core/signal_bus.py", "crates/uniai-kernel/", "uni_cortex/engine/kernel_scheduler.py"],
            verify_cmd="pytest -v tests/test_kernel_scheduler.py",
            depends_on=[],
            invariants=["ZERO_SIGNAL_DROP", "FAIL_CLOSED_DISPATCH", "LAW_000_NO_SHORTCUTS"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-KER-001",
            parent_id=m1_id,
            level="TASK",
            layer="LAYER_2_SYSTEMS",
            title="Preemptive Priority Process Scheduler & Context Swapper",
            description="Implement AIOS-grade priority queue scheduler with cooperative context-window paging and agent execution time slices.",
            target_files=["uni_cortex/engine/kernel_scheduler.py", "uni_life/core/signal_bus.py"],
            verify_cmd="python3 -c 'from uni_cortex.engine.kernel_scheduler import KernelProcessScheduler; print(\"OK\")'",
            depends_on=[],
            invariants=["PREEMPTIVE_FAIRNESS_INVARIANT"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-KER-002",
            parent_id=m1_id,
            level="TASK",
            layer="LAYER_1_DOMAIN",
            title="Unified Synaptic Bus Bridge & Protobuf CIR Telemetry",
            description="Translate runtime signals into binary Protobuf CIRPackets so active inference and causal engines observe verified system states.",
            target_files=["uni_core/cortex/telemetry_bridge.py", "uni_core/contracts/models.py"],
            verify_cmd="python3 -c 'from uni_core.cortex.telemetry_bridge import convert_signal_to_cir; print(\"OK\")'",
            depends_on=["TASK-KER-001"],
            invariants=["CIR_SCHEMA_PARITY"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-KER-003",
            parent_id=m1_id,
            level="TASK",
            layer="LAYER_2_SYSTEMS",
            title="Kernel & Synaptic Event Bus Verification Suite",
            description="Empirical integration harness proving sub-millisecond signal dispatch across 57 Green Primes under simulated burst loads.",
            target_files=["tests/test_kernel_scheduler.py"],
            verify_cmd="pytest -v tests/test_kernel_scheduler.py",
            depends_on=["TASK-KER-002"],
            invariants=["SUB_MS_DISPATCH_LATENCY"]
        ))

        # =========================================================================
        # PHASE 2: JAX ACTIVE INFERENCE & CAUSAL COUNTERFACTUAL ENGINE
        # =========================================================================
        m2_id = "M2-ACTIVE-INFERENCE"
        tasks.append(TaskDefinition(
            task_id=m2_id,
            parent_id=None,
            level="MILESTONE",
            layer="LAYER_5_INTELLIGENCE",
            title="Phase 2: JAX-Native Active Inference & Causal Counterfactual Engine",
            description="Scale Karl Friston Expected Free Energy (EFE) loops and Judea Pearl do-calculus causal abduction with Z3 SMT formal verification.",
            target_files=["uni_core/predictive/", "uni_core/reasoning/"],
            verify_cmd="pytest -v tests/test_active_inference_causal.py",
            depends_on=[m1_id],
            invariants=["EFE_MINIMIZATION_BOUND", "CONFIRMED_NOT_TRUTH_INVARIANT"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-ACT-001",
            parent_id=m2_id,
            level="TASK",
            layer="LAYER_5_INTELLIGENCE",
            title="Epistemic Curiosity & Expected Free Energy Policy Evaluator",
            description="Implement JAX-accelerated Expected Free Energy (EFE) minimization policy loop balancing epistemic information gain vs pragmatic goal execution.",
            target_files=["uni_core/predictive/efe_evaluator.py", "uni_core/predictive/cognitive_loop.py"],
            verify_cmd="python3 -c 'from uni_core.predictive.efe_evaluator import EFEEvaluator; print(\"OK\")'",
            depends_on=["TASK-KER-003"],
            invariants=["EFE_MATHEMATICAL_CONVERGENCE"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-ACT-002",
            parent_id=m2_id,
            level="TASK",
            layer="LAYER_5_INTELLIGENCE",
            title="Judea Pearl Structural Causal Model & Counterfactual Abduction Engine",
            description="Implement abductive diagnosis producing immutable competing hypothesis ledgers explaining system anomalies with Z3 formal safety proofs.",
            target_files=["uni_core/predictive/abductive_engine.py", "uni_core/formal/z3_verifier.py"],
            verify_cmd="python3 -c 'from uni_core.predictive.abductive_engine import AbductiveEngine; print(\"OK\")'",
            depends_on=["TASK-ACT-001"],
            invariants=["Z3_SMT_FORMAL_GATE"]
        ))

        # =========================================================================
        # PHASE 3: OFFLINE LOCAL SLM RUNTIME & GRAMMAR-CONSTRAINED DECODING
        # =========================================================================
        m3_id = "M3-LOCAL-REASONING"
        tasks.append(TaskDefinition(
            task_id=m3_id,
            parent_id=None,
            level="MILESTONE",
            layer="LAYER_5_INTELLIGENCE",
            title="Phase 3: Zero-API Offline SLM Runtime with Grammar Masking",
            description="Bind local quantized GGUF/ONNX engines with Context-Free Grammar (CFG) logit masking for 100% offline hallucination-free generation.",
            target_files=["uni_cortex/engine/local_model_runtime.py", "uni_cortex/engine/grammar_decoder.py"],
            verify_cmd="pytest -v tests/test_local_reasoning.py",
            depends_on=[m2_id],
            invariants=["ZERO_EXTERNAL_NETWORK", "GRAMMAR_INVARIANT_LOCK"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-SLM-001",
            parent_id=m3_id,
            level="TASK",
            layer="LAYER_5_INTELLIGENCE",
            title="Universal Quantized GGUF / ONNX High-Throughput Engine",
            description="Build low-latency local inference binding for qwen2.5-coder models with zero-copy tensor caching and sub-millisecond dispatch.",
            target_files=["uni_cortex/engine/local_model_runtime.py"],
            verify_cmd="python3 -c 'from uni_cortex.engine.local_model_runtime import LocalModelEngine; print(\"OK\")'",
            depends_on=["TASK-ACT-002"],
            invariants=["LOCAL_SOVEREIGNTY_AIRGAP"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-SLM-002",
            parent_id=m3_id,
            level="TASK",
            layer="LAYER_5_INTELLIGENCE",
            title="Context-Free Grammar (CFG) Logit Masking for Green Primes",
            description="Implement token logit masking guaranteeing 100% valid AST JSON schemas and typed contracts from the local model.",
            target_files=["uni_cortex/engine/grammar_decoder.py"],
            verify_cmd="python3 -c 'from uni_cortex.engine.grammar_decoder import GrammarConstrainedDecoder; print(\"OK\")'",
            depends_on=["TASK-SLM-001"],
            invariants=["ZERO_HALLUCINATED_SYNTAX"]
        ))

        # =========================================================================
        # PHASE 4: TACTILE SOVEREIGN MULTIMODAL TUI WORKBENCH
        # =========================================================================
        m4_id = "M4-TACTILE-TUI"
        tasks.append(TaskDefinition(
            task_id=m4_id,
            parent_id=None,
            level="MILESTONE",
            layer="LAYER_3_INTERFACE",
            title="Phase 4: Tactile Sovereign Multimodal TUI Workbench",
            description="Interactive high-contrast Bringhurst typography console (`main.py console`) featuring multi-pane telemetry and live thought streams.",
            target_files=["main.py", "uni_ui/console.py", "uni_ui/thought_stream.py"],
            verify_cmd="python3 main.py --help",
            depends_on=[m3_id],
            invariants=["OPTICAL_TYPOGRAPHY_BRINGHURST", "ZERO_DEVANAGARI"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-TUI-001",
            parent_id=m4_id,
            level="TASK",
            layer="LAYER_3_INTERFACE",
            title="Multi-Pane Holographic Terminal Dashboard (Rich/Textual)",
            description="Build real-time terminal workbench: Live System 2 Thought Stream, 57 Green Primes Telemetry, 5-Tier Memory Graph Recall, and Health Gauges.",
            target_files=["uni_ui/console.py", "uni_ui/layout.py"],
            verify_cmd="python3 -c 'from uni_ui.console import SovereignConsoleApp; print(\"OK\")'",
            depends_on=["TASK-SLM-002"],
            invariants=["WCAG_HIGH_CONTRAST_MONOCHROME"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-TUI-002",
            parent_id=m4_id,
            level="TASK",
            layer="LAYER_3_INTERFACE",
            title="Interactive Founder Conversational REPL & Command Dispatcher",
            description="Implement responsive prompt interface allowing Founder Shoeb Ahmad to issue tasks, query memory, and guide autonomous agent runs.",
            target_files=["uni_ui/repl.py", "main.py"],
            verify_cmd="python3 -c 'from uni_ui.repl import InteractiveREPL; print(\"OK\")'",
            depends_on=["TASK-TUI-001"],
            invariants=["ZERO_DEVANAGARI_ENFORCEMENT"]
        ))

        # =========================================================================
        # PHASE 5: AUTONOMOUS COMMERCIAL SHOWROOM SHIELD
        # =========================================================================
        m5_id = "M5-COMMERCIAL-SHIELD"
        tasks.append(TaskDefinition(
            task_id=m5_id,
            parent_id=None,
            level="MILESTONE",
            layer="LAYER_4_SECURITY",
            title="Phase 5: Autonomous Commercial Showroom Shield",
            description="Equip UniAI-OS with retail ERP capabilities: statutory GST vector PDF, inward distributor OCR, and integer paise ledger.",
            target_files=["crates/", "uni_cortex/engine/invoice_engine.py", "uni_cortex/primes/33_invoice_ocr_prime/"],
            verify_cmd="pytest -v tests/test_showroom_shield.py",
            depends_on=[m4_id],
            invariants=["INTEGER_PAISE_ACC_001", "GST_RULE_46_COMPLIANCE"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-SHW-001",
            parent_id=m5_id,
            level="TASK",
            layer="LAYER_1_DOMAIN",
            title="Statutory GST Vector PDF & Dynamic UPI QR Generator",
            description="Pure mathematical PDF bill generator with exact integer paise rounding (Law ACC-001) and ESC/POS direct thermal print bytes.",
            target_files=["uni_cortex/engine/invoice_pdf_engine.py"],
            verify_cmd="python3 -c 'from uni_cortex.engine.invoice_pdf_engine import VectorInvoiceGenerator; print(\"OK\")'",
            depends_on=["TASK-TUI-002"],
            invariants=["ZERO_FLOAT_MATH"]
        ))

        tasks.append(TaskDefinition(
            task_id="TASK-SHW-002",
            parent_id=m5_id,
            level="TASK",
            layer="LAYER_1_DOMAIN",
            title="Inward Distributor Wholesale Bill Multi-Format OCR Parser",
            description="Bind specialized OCR Green Prime to parse wholesale distributor bills (GTIN-14, batch, expiry, tax splits, HSN codes).",
            target_files=["uni_cortex/engine/distributor_ocr_engine.py"],
            verify_cmd="python3 -c 'from uni_cortex.engine.distributor_ocr_engine import DistributorOCREngine; print(\"OK\")'",
            depends_on=["TASK-SHW-001"],
            invariants=["GS1_GSR_823E_COMPLIANCE"]
        ))

        return tasks

    def compile_plan_to_unigov(self, tasks: List[TaskDefinition]) -> Tuple[int, int]:
        """Compile synthesized tasks directly into .unigov/state.db with cycle detection."""
        self.gov_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        from unigov.db import init_schema
        init_schema(conn)

        # Clear existing tasks
        conn.execute("DELETE FROM task_dependencies")
        conn.execute("DELETE FROM tasks")

        inserted_tasks = 0
        inserted_deps = 0

        for t in tasks:
            status = "READY" if (t.level == "TASK" and not t.depends_on) else "PENDING"
            conn.execute("""
                INSERT OR REPLACE INTO tasks (task_id, parent_id, level, layer, title, description, target_files_json, verify_cmd, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t.task_id,
                t.parent_id,
                t.level,
                t.layer,
                t.title,
                t.description,
                json.dumps(t.target_files),
                t.verify_cmd,
                status
            ))
            inserted_tasks += 1

        for t in tasks:
            for dep in t.depends_on:
                conn.execute(
                    "INSERT OR IGNORE INTO task_dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
                    (t.task_id, dep)
                )
                inserted_deps += 1

        conn.commit()
        conn.close()
        return inserted_tasks, inserted_deps

    def export_markdown_plan(self, tasks: List[TaskDefinition], out_path: Path):
        """Export structured roadmap into a beautiful Markdown document."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        md_lines = [
            "# 🌌 UniAI-OS v3.0.0: Sovereign Frontier Master Roadmap (2026–2030)",
            "",
            "**Architecture:** Active-Inference Neuro-Symbolic Agent Operating System (AN-AIOS)  ",
            "**Compiled via:** UniForge Pillar 11 (UniPlanner)  ",
            "**Governance Target:** `.unigov/state.db`  ",
            "**Architects:** Antigravity (Tera AI Bhai) & Founder Shoeb Ahmad (Shanu)  ",
            "",
            "---",
            "",
            "## 🎯 5 Strategic Phases Overview",
            "",
            "| Phase ID | Strategic Milestone | Layer | Dependencies | Initial State |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        for t in tasks:
            if t.level == "MILESTONE":
                deps = ", ".join(t.depends_on) or "None (Root)"
                md_lines.append(f"| **{t.task_id}** | {t.title} | `{t.layer}` | {deps} | `ACTIVE` |")

        md_lines.extend([
            "",
            "---",
            "",
            "## 📋 Hierarchical Task WBS & Verification Contracts",
            ""
        ])

        for t in tasks:
            if t.level == "MILESTONE":
                md_lines.extend([
                    f"### 🏆 {t.task_id}: {t.title}",
                    f"**Objective:** {t.description}  ",
                    f"**Layer:** `{t.layer}` | **Invariants:** {', '.join(t.invariants)}  ",
                    ""
                ])
            elif t.level == "TASK":
                deps = ", ".join(t.depends_on) or "None (Can Start Immediately)"
                targets = ", ".join([f"`{f}`" for f in t.target_files])
                md_lines.extend([
                    f"#### 🔹 `{t.task_id}`: {t.title}",
                    f"- **Scope & Architecture:** {t.description}",
                    f"- **Dependencies:** {deps}",
                    f"- **Target Files:** {targets}",
                    f"- **Verification Gate:** `{t.verify_cmd}`",
                    f"- **Hard Invariants:** {', '.join(t.invariants)}",
                    ""
                ])

        out_path.write_text("\n".join(md_lines), encoding="utf-8")
        console.print(f"[bold green]✓ Master roadmap markdown exported to {out_path}[/bold green]")

    def render_terminal_tree(self, tasks: List[TaskDefinition]):
        """Render Rich Tree visualization of the roadmap in terminal."""
        tree = Tree("⬢ [bold cyan]UniAI-OS 5-Tier Frontier Roadmap (AN-AIOS Master Plan)[/bold cyan]")
        
        milestone_nodes = {}
        for t in tasks:
            if t.level == "MILESTONE":
                m_node = tree.add(f"[bold green]{t.task_id}:[/bold green] [bold white]{t.title}[/bold white] [dim]({t.layer})[/dim]")
                milestone_nodes[t.task_id] = m_node

        for t in tasks:
            if t.level == "TASK":
                parent_node = milestone_nodes.get(t.parent_id, tree)
                status_color = "green" if not t.depends_on else "yellow"
                status_text = "READY TO EXECUTE" if not t.depends_on else "BLOCKED (PENDING DEPS)"
                parent_node.add(
                    f"[{status_color}]• {t.task_id}:[/{status_color}] {t.title} "
                    f"[{status_color}][{status_text}][/{status_color}]"
                )

        console.print("\n")
        console.print(tree)
        console.print("\n")
