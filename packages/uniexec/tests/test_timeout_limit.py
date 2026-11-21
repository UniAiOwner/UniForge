"""
Unit tests for UniExec Tier 3: Timeout & Resource Limits
"""

import pytest
from uniexec.engine import get_engine


def test_sandbox_infinite_loop_timeout():
    engine = get_engine()
    # Script that runs an infinite loop
    script = """
while True:
    pass
"""
    # Hard timeout set to 2 seconds
    res = engine.execute(script, timeout_seconds=2)
    assert res.status == "TIMEOUT"
    assert "timeout limit" in res.error.lower()
    assert res.result is None
