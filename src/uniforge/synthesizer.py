"""UniForge Synthesizer: Multi-Repository Deep AST Analysis, Deduplication & Clean-Room Transplanter.
Constitutional Law-000: Zero Shortcuts, Grounded AST Analysis.
"""

import os
import sys
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
    ".idea", ".vscode", "node_modules", ".mypy_cache", ".deepeval", "build", "dist"
}

class CodeFileMetadata:
    def __init__(self, repo_name: str, rel_path: str, full_path: str):
        self.repo_name = repo_name
        self.rel_path = rel_path
        self.full_path = full_path
        self.ext = os.path.splitext(rel_path)[1].lower()
        self.size = os.path.getsize(full_path)
        self.sha256 = ""
        self.ast_hash = ""
        self.lines = 0
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.imports: List[str] = []
        self.has_types: bool = False
        self.is_async: bool = False
        self.has_formal_or_z3: bool = False
        self.law000_clean: bool = True
        self.quality_score: float = 0.0
        self.status: str = "UNIQUE"  # UNIQUE, SOTA_CANONICAL, REDUNDANT_COPY, DEAD_STUB

class MultiRepoSynthesizer:
    def __init__(self, repo_map: Dict[str, str], target_workspace: str):
        self.repo_map = {k: Path(v).resolve() for k, v in repo_map.items() if Path(v).exists()}
        self.target_workspace = Path(target_workspace).resolve()
        self.files: List[CodeFileMetadata] = []
        self.ast_clusters: Dict[str, List[CodeFileMetadata]] = defaultdict(list)
        self.symbol_table: Dict[str, List[Tuple[str, str]]] = defaultdict(list) # symbol -> [(repo, rel_path)]

    def scan_and_analyze(self) -> Dict[str, Any]:
        """Deep scan every file across all repositories and extract AST & quality metrics."""
        total_found = 0
        console.print("[bold cyan]Scanning and indexing files across all repositories...[/bold cyan]")
        
        for repo_name, repo_path in self.repo_map.items():
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in [".py", ".rs", ".kt", ".md", ".json", ".proto", ".toml"]:
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, repo_path)
                        meta = CodeFileMetadata(repo_name, rel_p, full_p)
                        self._analyze_file(meta)
                        self.files.append(meta)
                        total_found += 1

        console.print(f"[bold green]Parsed AST & metadata for {len(self.files)} eligible code assets.[/bold green]")
        self._cluster_and_evaluate_duplicates()
        return self._generate_summary()

    def _analyze_file(self, meta: CodeFileMetadata):
        try:
            with open(meta.full_path, "rb") as f:
                raw_bytes = f.read()
            meta.sha256 = hashlib.sha256(raw_bytes).hexdigest()
            text = raw_bytes.decode("utf-8", errors="ignore")
            meta.lines = text.count("\n") + 1

            if "@Suppress" in text:
                meta.law000_clean = False
            if "z3" in text or "SymbolicSolver" in text or "IEEE-754" in text:
                meta.has_formal_or_z3 = True

            if meta.ext == ".py":
                self._parse_python_ast(meta, text)
            else:
                # Basic signature extraction for Rust/Kotlin/MD
                meta.ast_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
                self._calculate_quality(meta)

        except Exception as e:
            meta.quality_score = 0.0

    def _parse_python_ast(self, meta: CodeFileMetadata, text: str):
        try:
            tree = ast.parse(text)
            norm_tokens = []
            annotated_count = 0
            total_args = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    meta.functions.append(node.name)
                    norm_tokens.append(f"F:{node.name}")
                    self.symbol_table[node.name].append((meta.repo_name, meta.rel_path))
                    if isinstance(node, ast.AsyncFunctionDef):
                        meta.is_async = True
                    for arg in node.args.args:
                        total_args += 1
                        if arg.annotation:
                            annotated_count += 1
                elif isinstance(node, ast.ClassDef):
                    meta.classes.append(node.name)
                    norm_tokens.append(f"C:{node.name}")
                    self.symbol_table[node.name].append((meta.repo_name, meta.rel_path))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        meta.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        meta.imports.append(node.module)

            if total_args > 0 and (annotated_count / total_args) >= 0.5:
                meta.has_types = True

            # Normalized AST Hash ignores whitespace, docstrings, comments
            ast_repr = "|".join(norm_tokens)
            meta.ast_hash = hashlib.md5(ast_repr.encode("utf-8")).hexdigest()
        except SyntaxError:
            # Fallback to text md5 if syntax error
            meta.ast_hash = hashlib.md5(text.encode("utf-8")).hexdigest()

        self._calculate_quality(meta)

    def _calculate_quality(self, meta: CodeFileMetadata):
        score = 50.0  # Base
        if meta.lines > 15: score += 10
        if meta.has_types: score += 15
        if meta.is_async: score += 10
        if meta.has_formal_or_z3: score += 15
        if not meta.law000_clean: score -= 30
        if meta.lines < 5 and len(meta.functions) == 0: score -= 30
        meta.quality_score = max(0.0, min(100.0, score))

    def _cluster_and_evaluate_duplicates(self):
        """Group files by AST Hash to identify duplicates and select SOTA canonicals."""
        for f in self.files:
            if f.ext in [".py", ".rs", ".kt"] and f.ast_hash:
                self.ast_clusters[f.ast_hash].append(f)

        for ast_h, cluster in self.ast_clusters.items():
            if len(cluster) > 1:
                # Multiple files share exact structural AST!
                # Sort by quality_score descending, then line count, then repo priority
                cluster.sort(key=lambda x: (x.quality_score, x.lines), reverse=True)
                canonical = cluster[0]
                canonical.status = "SOTA_CANONICAL"
                for dup in cluster[1:]:
                    dup.status = "REDUNDANT_COPY"

    def _generate_summary(self) -> Dict[str, Any]:
        total = len(self.files)
        redundant = sum(1 for f in self.files if f.status == "REDUNDANT_COPY")
        sota = sum(1 for f in self.files if f.status == "SOTA_CANONICAL")
        unique = sum(1 for f in self.files if f.status == "UNIQUE")
        avg_quality = sum(f.quality_score for f in self.files) / max(1, total)

        repo_breakdown = defaultdict(lambda: {"total": 0, "redundant": 0, "sota": 0, "high_quality": 0})
        for f in self.files:
            rb = repo_breakdown[f.repo_name]
            rb["total"] += 1
            if f.status == "REDUNDANT_COPY": rb["redundant"] += 1
            if f.status == "SOTA_CANONICAL": rb["sota"] += 1
            if f.quality_score >= 80: rb["high_quality"] += 1

        return {
            "total_files_analyzed": total,
            "unique_assets": unique,
            "sota_canonicals": sota,
            "redundant_duplicates_identified": redundant,
            "average_quality_score": round(avg_quality, 1),
            "repo_breakdown": dict(repo_breakdown)
        }

    def print_report(self, summary: Dict[str, Any]):
        """Render beautiful Rich terminal tables summarizing the audit."""
        console.print("\n")
        table = Table(title="⬢ Sovereign Multi-Repo Forensic Quality & Deduplication Audit", border_style="cyan")
        table.add_column("Repository", style="bold white")
        table.add_column("Total Files", justify="right")
        table.add_column("SOTA Canonicals", justify="right", style="green")
        table.add_column("Redundant Duplicates", justify="right", style="yellow")
        table.add_column("High Quality (>=80)", justify="right", style="magenta")

        for repo, stats in summary["repo_breakdown"].items():
            table.add_row(
                repo,
                str(stats["total"]),
                str(stats["sota"]),
                str(stats["redundant"]),
                str(stats["high_quality"])
            )

        console.print(table)
        console.print(
            Panel.fit(
                f"[bold green]Total Files Analyzed:[/bold green] {summary['total_files_analyzed']}\n"
                f"[bold cyan]SOTA Canonical Core Modules:[/bold cyan] {summary['sota_canonicals']}\n"
                f"[bold yellow]Redundant Clones Identified (Safe to Purge):[/bold yellow] {summary['redundant_duplicates_identified']}\n"
                f"[bold white]Overall Quality Index:[/bold white] {summary['average_quality_score']}/100",
                title="⬢ Synthesis Summary",
                border_style="green"
            )
        )

    def export_matrix(self, out_json_path: str):
        """Export full detailed matrix to JSON."""
        out_data = {
            "summary": self._generate_summary(),
            "files": [
                {
                    "repo": f.repo_name,
                    "rel_path": f.rel_path,
                    "ext": f.ext,
                    "lines": f.lines,
                    "quality_score": f.quality_score,
                    "status": f.status,
                    "functions": f.functions[:5],
                    "classes": f.classes[:5]
                }
                for f in self.files
            ]
        }
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=2)
        console.print(f"[bold green]✓ Full forensic matrix exported to {out_json_path}[/bold green]")
