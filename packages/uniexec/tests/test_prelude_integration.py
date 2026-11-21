"""
Unit tests for UniExec Prelude: Pre-Bound Primitives Integration
"""

import pytest
from uniexec.engine import get_engine


def test_prelude_get_beacon():
    engine = get_engine()
    script = """
b = get_beacon()
result = {
    'mission': b.get('mission_name'),
    'status': b.get('status')
}
"""
    res = engine.execute(script, timeout_seconds=5)
    assert res.status == "SUCCESS"
    assert res.result is not None
    assert res.result.get("mission") == "UniCortex Brain 2.0"
    assert res.result.get("status") == "ACTIVE"


def test_prelude_check_drift_allowed():
    engine = get_engine()
    script = """
chk = check_drift(target_path="uniexec/sandbox.py", intent_summary="build sandbox")
result = chk.get('allowed')
"""
    res = engine.execute(script, timeout_seconds=5)
    assert res.status == "SUCCESS"
    assert res.result is True


def test_prelude_verify_code_gate():
    engine = get_engine()
    script = """
code = '''
\"\"\"Square function.\"\"\"
def sq(x: int) -> int:
    assert x >= 0
    return x * x
'''
gate_output = verify_code_gate(code, filename="math.py")
result = 'RATIFIED' in gate_output
"""
    res = engine.execute(script, timeout_seconds=8)
    assert res.status == "SUCCESS"
    assert res.result is True


def test_prelude_memory_recall():
    engine = get_engine()
    script = """
mem_out = memory_recall("accounting paise", top_k=2)
result = len(mem_out) > 0 and 'MEMORY RECALL' in mem_out
"""
    res = engine.execute(script, timeout_seconds=8)
    assert res.status == "SUCCESS"
    assert res.result is True
