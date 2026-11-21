"""
Unit tests for UniExec Tier 2: Bubblewrap Namespace Isolation
"""

import pytest
from uniexec.engine import get_engine


def test_sandbox_pure_computation():
    engine = get_engine()
    script = """
a = 15
b = 27
result = a * b
"""
    res = engine.execute(script, timeout_seconds=5)
    assert res.status == "SUCCESS"
    assert res.result == 405
    assert res.execution_time_ms > 0


def test_sandbox_readonly_filesystem():
    engine = get_engine()
    # Attempt to write to /usr or /etc must fail with Read-only file system (OSError)
    script = """
try:
    with open('/usr/test_write.txt', 'w') as f:
        f.write('malicious')
    result = 'WROTE_SUCCESS'
except Exception as e:
    result = f'BLOCKED: {type(e).__name__}'
"""
    res = engine.execute(script, timeout_seconds=5)
    assert res.status == "SUCCESS"
    assert "BLOCKED: OSError" in str(res.result) or "BLOCKED: PermissionError" in str(res.result)


def test_sandbox_tmp_is_writable():
    engine = get_engine()
    # /tmp is an isolated in-memory tmpfs and should allow writing temporary scratch files
    script = """
with open('/tmp/scratch.txt', 'w') as f:
    f.write('temporary scratchpad')

with open('/tmp/scratch.txt', 'r') as f:
    content = f.read()

result = content
"""
    res = engine.execute(script, timeout_seconds=5)
    assert res.status == "SUCCESS"
    assert res.result == "temporary scratchpad"
