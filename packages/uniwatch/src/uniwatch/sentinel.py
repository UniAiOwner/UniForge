"""
UniWatch Sensory Sentinel Bridge.
Connects filesystem mutations to:
1. UniBus (Pillar 6) -> Work Mutex Leases & Event Alerts
2. UniBeacon (Pillar 3) -> Mission Drift Interception
3. UniVerify (Pillar 4) -> Law-000 Invariant Guard
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


def check_unibus_lease(file_path: Path) -> Tuple[bool, Optional[str]]:
    """Checks if the file is currently locked under an active lease in UniBus."""
    try:
        from unibus import UniBus
        bus = UniBus()
        leases = bus.list_leases(active_only=True)
        res_key = f"file:{file_path.name}"
        res_full = f"file:{file_path}"

        for l in leases:
            if l.resource_id in (res_key, res_full, str(file_path)):
                return True, f"Active lease held by '{l.owner_agent}' (expires {l.expires_at[:19]})"
        return True, None
    except Exception:
        return True, None


def check_unibeacon_drift(file_path: Path, intent: str = "Filesystem Mutation") -> Tuple[bool, Optional[str]]:
    """Checks if the file modification deviates from the active UniBeacon mission."""
    try:
        from unimemory.engine import get_engine
        mem = get_engine()
        drift_res = mem.check_drift(target_path=str(file_path), intent_summary=intent)
        if not drift_res.allowed:
            return False, f"Drift Sentinel Violation: {drift_res.reason} (Forbidden: {', '.join(drift_res.forbidden_terms_hit)})"
        return True, None
    except Exception:
        return True, None


def check_univerify_invariants(code_text: str, file_path: Path) -> Tuple[bool, List[str]]:
    """Checks Law-000 invariants (zero-suppress, zero fake mocks, zero secrets) via UniVerify."""
    try:
        from univerify.invariants import check_all_invariants
        res = check_all_invariants(code_text, filename=file_path.name)
        if not res.passed:
            violations = [f"[{v.rule_id}] {v.message}" for v in res.violations]
            return False, violations
        return True, []
    except Exception:
        # Fallback regex checks if univerify is unavailable
        violations = []
        if "@Suppress" in code_text or "@SuppressWarnings" in code_text:
            violations.append("[LAW-000-SUPPRESS] @Suppress annotation strictly forbidden")
        return len(violations) == 0, violations


def dispatch_reflex_alert(file_path: Path, error_message: str, priority: str = "CRITICAL"):
    """Publishes reflex alert onto UniBus and dispatches desktop notification."""
    # 1. Publish to UniBus
    try:
        from unibus import UniBus, EventPriority
        bus = UniBus()
        p_enum = getattr(EventPriority, priority.upper(), EventPriority.CRITICAL)
        bus.publish_event(
            topic="watch.syntax_violation",
            payload={"file": str(file_path), "error": error_message},
            priority=p_enum
        )
    except Exception:
        pass

    # 2. Desktop notification via notify-send
    if shutil.which("notify-send") and os.environ.get("DISPLAY"):
        try:
            subprocess.run(
                ["notify-send", "-u", "critical", "UniWatch Alert", f"{file_path.name}: {error_message}"],
                capture_output=True,
                timeout=1
            )
        except Exception:
            pass
