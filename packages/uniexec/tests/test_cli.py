"""
Unit tests for UniExec Typer CLI
"""

import pytest
from typer.testing import CliRunner
from uniexec.cli import app

runner = CliRunner()


def test_cli_version():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "UniExec" in res.stdout
    assert "2611.19123" in res.stdout


def test_cli_eval():
    res = runner.invoke(app, ["eval", "result = 100 * 5"])
    assert res.exit_code == 0
    assert "SUCCESS" in res.stdout
    assert "500" in res.stdout


def test_cli_doctor():
    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert "HEALTHY" in res.stdout


def test_cli_benchmark():
    res = runner.invoke(app, ["benchmark"])
    assert res.exit_code == 0
    assert "reduction" in res.stdout
