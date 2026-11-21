"""
Unit Tests for UniMemory CLI Commands
=====================================
"""

from typer.testing import CliRunner
from unimemory.cli import app

runner = CliRunner()


def test_cli_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "UniMemory Substrate Health" in result.stdout
    assert "HEALTHY" in result.stdout


def test_cli_store_and_recall():
    res_store = runner.invoke(app, ["store", "Z3_Solver", "proves", "Mathematical_Invariants"])
    assert res_store.exit_code == 0
    assert "Stored Fact" in res_store.stdout

    res_recall = runner.invoke(app, ["recall", "Z3_Solver"])
    assert res_recall.exit_code == 0
    assert "MEMORY RECALL FOR" in res_recall.stdout


def test_cli_episode():
    res = runner.invoke(app, ["episode", "UniTerminal", "Compile Winit App", "Always run package script after cargo build", "--status", "SUCCESS"])
    assert res.exit_code == 0
    assert "Recorded Episode" in res.stdout


def test_cli_working():
    res = runner.invoke(app, ["working", "active_project", "UniMemory", "--project", "GLOBAL"])
    assert res.exit_code == 0
    assert "Stored Working Context" in res.stdout


def test_cli_status():
    res = runner.invoke(app, ["status"])
    assert res.exit_code == 0
    assert "Active Working Context" in res.stdout
