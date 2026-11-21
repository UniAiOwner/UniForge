"""
Unit tests for UniVerify Typer CLI
"""

import pytest
from typer.testing import CliRunner
from univerify.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "UniVerify" in result.stdout


def test_cli_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "100% healthy" in result.stdout


def test_cli_prove_loop():
    result = runner.invoke(app, ["prove-loop", "100"])
    assert result.exit_code == 0
    assert "PROVEN" in result.stdout


def test_cli_prove_bounds_valid():
    result = runner.invoke(app, ["prove-bounds", "100", "0", "99"])
    assert result.exit_code == 0
    assert "PROVEN" in result.stdout


def test_cli_prove_bounds_invalid():
    result = runner.invoke(app, ["prove-bounds", "100", "0", "100"])
    assert result.exit_code == 1
    assert "VIOLATION" in result.stdout
