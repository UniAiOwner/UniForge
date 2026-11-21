"""
Tests for UniBus CLI Commands.
"""

from typer.testing import CliRunner
from unibus.cli import app

runner = CliRunner()


def test_cli_version():
    res = runner.invoke(app, ["--version"])
    assert res.exit_code == 0
    assert "UniBus version" in res.stdout


def test_cli_doctor():
    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert "UniBus Diagnostic Report" in res.stdout


def test_cli_status():
    res = runner.invoke(app, ["status"])
    assert res.exit_code == 0
    assert "UniBus System State" in res.stdout


def test_cli_constraint_flow():
    # Set
    set_res = runner.invoke(app, ["constraint", "set", "TEST_KEY", "123", "--domain", "SECURITY", "--unit", "ms"])
    assert set_res.exit_code == 0
    assert "Constraint Set" in set_res.stdout

    # Get
    get_res = runner.invoke(app, ["constraint", "get", "TEST_KEY"])
    assert get_res.exit_code == 0
    assert "TEST_KEY" in get_res.stdout

    # List
    list_res = runner.invoke(app, ["constraint", "list", "--domain", "SECURITY"])
    assert list_res.exit_code == 0
    assert "TEST_KEY" in list_res.stdout


def test_cli_decision_flow():
    log_res = runner.invoke(app, ["decision", "log", "Test ADR Title", "--rationale", "Test Rationale"])
    assert log_res.exit_code == 0
    assert "ADR Recorded" in log_res.stdout

    list_res = runner.invoke(app, ["decision", "list"])
    assert list_res.exit_code == 0
    assert "Test ADR Title" in list_res.stdout


def test_cli_lease_flow():
    # Acquire
    acq_res = runner.invoke(app, ["lease", "acquire", "test:resource", "--owner", "cli_agent", "--ttl", "30"])
    assert acq_res.exit_code == 0
    assert "Lease Acquired" in acq_res.stdout

    # List
    list_res = runner.invoke(app, ["lease", "list"])
    assert list_res.exit_code == 0
    assert "test:resource" in list_res.stdout

    # Release
    rel_res = runner.invoke(app, ["lease", "release", "test:resource"])
    assert rel_res.exit_code == 0
    assert "Lease Released" in rel_res.stdout


def test_cli_event_flow():
    # Publish
    pub_res = runner.invoke(app, ["event", "publish", "cli.test.event", '{"status": "ok"}', "--priority", "HIGH"])
    assert pub_res.exit_code == 0
    assert "Event Published" in pub_res.stdout

    # Poll
    poll_res = runner.invoke(app, ["event", "poll", "--topic", "cli.test.event"])
    assert poll_res.exit_code == 0
    assert "cli.test.event" in poll_res.stdout


def test_cli_agent_heartbeat():
    hb_res = runner.invoke(app, ["agent", "heartbeat", "test_prime", "--task", "verifying"])
    assert hb_res.exit_code == 0
    assert "Heartbeat Recorded" in hb_res.stdout

    list_res = runner.invoke(app, ["agent", "list"])
    assert list_res.exit_code == 0
    assert "test_prime" in list_res.stdout
