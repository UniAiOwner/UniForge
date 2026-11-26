"""Automated unit & integration tests for UniForge Genesis (Vision-to-Blueprint & Skeleton Engine)."""

import sqlite3
import tempfile
from pathlib import Path

from uniforge.genesis import VisionGenesisArchitect


def test_retail_pos_vision_categorization_and_android_stack() -> None:
    architect = VisionGenesisArchitect()
    bp = architect.generate_blueprint(
        "Ek offline-first mobile showroom POS billing aur stock inventory app chahiye",
        project_name="ShowroomPOS",
    )
    assert bp.vision.domain == "RETAIL_POS"
    assert bp.vision.offline_first is True
    assert "Android" in bp.vision.target_platforms
    assert bp.tech_stack.stack_id == "android_compose_room"
    assert len(bp.ui_ux.screens) >= 4
    assert all(len(s.states) == 5 for s in bp.ui_ux.screens)


def test_saas_web_vision_recommends_nextjs_postgres() -> None:
    architect = VisionGenesisArchitect()
    bp = architect.generate_blueprint(
        "Build a multi-tenant SaaS CRM web portal and analytics dashboard",
        project_name="PulseCRM",
    )
    assert bp.vision.domain == "SAAS_WEB"
    assert bp.tech_stack.stack_id == "nextjs_postgres"
    assert "Frontend" in bp.tech_stack.primary_stack


def test_cli_vision_recommends_python_cli_and_scaffolds_runnable_project() -> None:
    architect = VisionGenesisArchitect()
    bp = architect.generate_blueprint(
        "Build a portable developer CLI automation tool for project checks",
        project_name="DevCheckCLI",
    )
    assert bp.vision.domain == "CLI_DEVTOOL"
    assert bp.tech_stack.stack_id == "python_cli"

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        md_path = architect.export_blueprint_markdown(bp, root / "PLANNING" / "MASTER_ARCHITECTURE_BLUEPRINT.md")
        assert md_path.exists()
        assert "DevCheckCLI" in md_path.read_text(encoding="utf-8")

        task_count = architect.register_unigov_tasks(bp, root)
        assert task_count >= 5
        db_path = root / ".unigov" / "state.db"
        assert db_path.exists()
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        conn.close()
        assert rows == task_count

        created = architect.scaffold_skeleton(bp, root)
        assert "pyproject.toml" in created
        assert "tests/test_smoke.py" in created
        assert (root / "src" / "devcheckcli" / "domain" / "models.py").exists()
