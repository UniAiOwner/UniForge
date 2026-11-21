"""
Unit tests for UniVerify Level 2: Z3 SMT Formal Mathematical Code Verifier
"""

import pytest
from univerify.z3_prover import FormalZ3Prover


def test_loop_termination_proven():
    prover = FormalZ3Prover()
    res = prover.prove_loop_termination(max_iterations=100, decrement_step=1, break_condition_guaranteed=True)
    assert res.is_satisfied
    assert res.proof_status == "PROVEN"
    assert "strictly terminates" in res.mathematical_rationale


def test_loop_termination_refuted_when_no_break_condition():
    prover = FormalZ3Prover()
    res = prover.prove_loop_termination(max_iterations=100, decrement_step=1, break_condition_guaranteed=False)
    assert not res.is_satisfied
    assert res.proof_status == "VIOLATION_DETECTED"
    assert res.counter_example == {"break_condition": False}


def test_buffer_index_bounds_proven():
    prover = FormalZ3Prover()
    # Size 1024, accessing range [0, 1023] is safe
    res = prover.prove_buffer_index_bounds(buffer_size=1024, min_access_index=0, max_access_index=1023)
    assert res.is_satisfied
    assert res.proof_status == "PROVEN"
    assert res.counter_example is None


def test_buffer_index_bounds_violation_negative_index():
    prover = FormalZ3Prover()
    # Accessing -1 in buffer size 100
    res = prover.prove_buffer_index_bounds(buffer_size=100, min_access_index=-1, max_access_index=50)
    assert not res.is_satisfied
    assert res.proof_status == "VIOLATION_DETECTED"
    assert res.counter_example is not None


def test_buffer_index_bounds_violation_overflow():
    prover = FormalZ3Prover()
    # Size 100, accessing index 100 (which is out of bounds [0, 99])
    res = prover.prove_buffer_index_bounds(buffer_size=100, min_access_index=0, max_access_index=100)
    assert not res.is_satisfied
    assert res.proof_status == "VIOLATION_DETECTED"
    assert "violates size 100" in res.mathematical_rationale


def test_state_machine_transition_valid():
    prover = FormalZ3Prover()
    states = ["IDLE", "ANALYZING", "EXECUTING", "VERIFYING", "DONE"]
    transitions = {
        "IDLE": ["ANALYZING"],
        "ANALYZING": ["EXECUTING", "IDLE"],
        "EXECUTING": ["VERIFYING"],
        "VERIFYING": ["DONE", "EXECUTING"],
        "DONE": ["IDLE"]
    }
    res = prover.prove_state_machine_transition(states, "EXECUTING", "VERIFYING", transitions)
    assert res.is_satisfied
    assert res.proof_status == "PROVEN"


def test_state_machine_transition_illegal():
    prover = FormalZ3Prover()
    states = ["IDLE", "ANALYZING", "EXECUTING", "VERIFYING", "DONE"]
    transitions = {
        "IDLE": ["ANALYZING"],
        "ANALYZING": ["EXECUTING", "IDLE"],
        "EXECUTING": ["VERIFYING"],
        "VERIFYING": ["DONE", "EXECUTING"],
        "DONE": ["IDLE"]
    }
    # Direct jump from IDLE to DONE is illegal
    res = prover.prove_state_machine_transition(states, "IDLE", "DONE", transitions)
    assert not res.is_satisfied
    assert res.proof_status == "VIOLATION_DETECTED"
    assert "Illegal transition" in res.mathematical_rationale
