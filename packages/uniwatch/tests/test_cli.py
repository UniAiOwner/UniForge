"""
Tests for UniWatch CLI Commands.
"""

from pathlib import Path
from typer.testing import CliRunner
from uniwatch.cli import app

runner = CliRunner()


def test_cli_version():
    res = runner.invoke(app, ["--version"])
    assert res.exit_code == 0
    assert "UniWatch version" in res.stdout


def test_cli_doctor():
    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert "UniWatch Diagnostic Report" in res.stdout


def test_cli_status():
    res = runner.invoke(app, ["status"])
    assert res.exit_code == 0
    assert "UniWatch Status" in res.stdout


def test_cli_check_valid_file(tmp_path: Path):
    f = tmp_path / "Valid.kt"
    f.write_text("class Valid { fun foo() = 1 }\n")
    res = runner.invoke(app, ["check", str(f)])
    assert res.exit_code == 0
    assert "PASS" in res.stdout


def test_cli_check_invalid_syntax_file(tmp_path: Path):
    f = tmp_path / "Broken.kt"
    f.write_text("class Broken { fun foo() = 1 \n")  # missing brace
    res = runner.invoke(app, ["check", str(f)])
    assert res.exit_code == 1
    assert "VIOLATIONS FOUND" in res.stdout
