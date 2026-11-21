"""
Comprehensive Unit Test Suite for Sovereign Coding Triad.
Verifies Python, Kotlin, and Security specialists along with Substrate integrations.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sovereign_triad.models import FindingSeverity, TriadLanguage
from sovereign_triad.python_specialist import PythonSpecialist
from sovereign_triad.kotlin_specialist import KotlinSpecialist
from sovereign_triad.security_specialist import SecuritySpecialist
from sovereign_triad.triad_orchestrator import SovereignTriadOrchestrator


def test_python_specialist_clean_code():
    """Verify clean Python async code passes audit with zero critical findings."""
    clean_code = """
import asyncio

async def fetch_user_data(user_id: int) -> dict:
    await asyncio.sleep(0.01)
    return {"user_id": user_id, "status": "active"}
"""
    specialist = PythonSpecialist()
    report = specialist.audit_code(clean_code, file_path="user_service.py")
    assert report.passed is True
    assert report.critical_count == 0


def test_python_specialist_blocking_detection():
    """Verify blocking time.sleep and except: pass are caught as critical."""
    bad_code = """
import time

async def process_batch():
    time.sleep(2)  # Blocking!
    try:
        do_work()
    except:
        pass  # Silent suppression!
"""
    specialist = PythonSpecialist()
    report = specialist.audit_code(bad_code, file_path="bad_service.py")
    assert report.passed is False
    rule_ids = [f.rule_id for f in report.findings]
    assert "PY-ASYNC-BLOCKING-001" in rule_ids
    assert "LAW-000-SILENT-PASS" in rule_ids


def test_kotlin_specialist_zero_suppress():
    """Verify @Suppress annotation is strictly rejected under Law-000."""
    kt_code = """
package com.uniai.pos

@Suppress("UNCHECKED_CAST")
class PaymentHandler {
    fun handle() {}
}
"""
    specialist = KotlinSpecialist()
    report = specialist.audit_code(kt_code, file_path="PaymentHandler.kt")
    assert report.passed is False
    assert any(f.rule_id == "LAW-000-ZERO-SUPPRESS" for f in report.findings)


def test_kotlin_specialist_float_money():
    """Verify Float/Double money in financial models violates Law ACC-001."""
    financial_code = """
package com.uniai.invoice

data class InvoiceItem(
    val id: String,
    val amount: Double
)
"""
    specialist = KotlinSpecialist()
    report = specialist.audit_code(financial_code, file_path="InvoiceItem.kt")
    assert report.passed is False
    assert any(f.rule_id == "LAW-ACC-001-FLOAT-MONEY" for f in report.findings)


def test_security_specialist_secret_hunter():
    """Verify high-entropy secret detection with Shannon entropy."""
    high_entropy_token = "K9zX8bQ2wV7mP1yR4tL6jN0sD3fG5hA9"
    code_with_secret = f'secret_key = "{high_entropy_token}"\n'

    specialist = SecuritySpecialist()
    scan_res = specialist.scan_secrets(code_with_secret, file_path="config.py")
    assert scan_res.safe is False
    assert len(scan_res.secrets_found) > 0
    assert scan_res.secrets_found[0].shannon_entropy > 4.0


def test_security_specialist_z3_solver():
    """Verify Z3 SMT prover proves non-negative balance invariant."""
    specialist = SecuritySpecialist()
    res = specialist.verify_financial_non_negative_balance(
        initial_balance=1000,
        debit_amount=500,
        credit_amount=200
    )
    assert res.invariant_proved is True
    assert res.counterexample is None


def test_orchestrator_full_certification_pipeline():
    """Verify end-to-end certification through Sovereign Triad Orchestrator."""
    orchestrator = SovereignTriadOrchestrator()

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("""
import asyncio

async def compute_total(items: list[int]) -> int:
    await asyncio.sleep(0.001)
    return sum(items)
""")
        temp_file = f.name

    try:
        cert = orchestrator.verify_and_certify(temp_file)
        assert cert.overall_passed is True
        assert cert.syntax_valid is True
        assert cert.security_valid is True
        assert cert.invariants_valid is True
        assert cert.artifact_soundness_score >= 0.75
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
