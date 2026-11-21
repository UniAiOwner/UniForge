"""
UniWatch Event Loop & Debounced Reflex Dispatcher.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable

from uniwatch.config import MONITORED_EXTENSIONS, DEFAULT_DEBOUNCE_MS, MAX_SCAN_BYTES
from uniwatch.inotify import NativeInotify
from uniwatch.parsers import validate_file_syntax
from uniwatch.sentinel import (
    check_unibus_lease,
    check_unibeacon_drift,
    check_univerify_invariants,
    dispatch_reflex_alert,
)


class FileWatchAuditResult:
    def __init__(self, file_path: Path, is_passed: bool, errors: List[str], warnings: List[str]):
        self.file_path = file_path
        self.is_passed = is_passed
        self.errors = errors
        self.warnings = warnings


def audit_file(path: Path) -> FileWatchAuditResult:
    """Synchronous full-spectrum audit of a single file."""
    errors: List[str] = []
    warnings: List[str] = []

    if not path.exists() or not path.is_file():
        return FileWatchAuditResult(path, False, [f"File not found: {path}"], [])

    if path.suffix.lower() not in MONITORED_EXTENSIONS:
        return FileWatchAuditResult(path, True, [], [])

    try:
        size = path.stat().st_size
        if size > MAX_SCAN_BYTES:
            warnings.append(f"Skipping large file ({size} bytes > {MAX_SCAN_BYTES})")
            return FileWatchAuditResult(path, True, [], warnings)
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return FileWatchAuditResult(path, False, [f"Failed to read file: {e}"], [])

    # 1. Delimiter & Syntax Validation
    syntax_ok, syntax_err = validate_file_syntax(path)
    if not syntax_ok and syntax_err:
        errors.append(syntax_err)

    # 2. Law-000 Invariant Checks (Zero @Suppress, Zero fake mocks, Zero secrets)
    inv_ok, inv_violations = check_univerify_invariants(content, path)
    if not inv_ok:
        errors.extend(inv_violations)

    # 3. UniBeacon Mission Drift Check
    drift_ok, drift_warn = check_unibeacon_drift(path)
    if not drift_ok and drift_warn:
        errors.append(drift_warn)

    # 4. UniBus Lease Status Check
    lease_ok, lease_warn = check_unibus_lease(path)
    if lease_warn:
        warnings.append(lease_warn)

    is_passed = len(errors) == 0
    return FileWatchAuditResult(path, is_passed, errors, warnings)


class WatcherLoop:
    """Continuous Inotify Watcher Loop with debouncing and reflex alerts."""

    def __init__(
        self,
        root_dir: Path,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        on_violation: Optional[Callable[[FileWatchAuditResult], None]] = None
    ):
        self.root_dir = Path(root_dir).resolve()
        self.debounce_ms = debounce_ms
        self.on_violation = on_violation or (lambda res: None)
        self.inotify = NativeInotify()
        self.is_running = False
        self.last_seen_times: Dict[str, float] = {}
        self.total_scans = 0
        self.total_violations = 0

    def start(self, max_events: Optional[int] = None):
        """Starts monitoring. If max_events is set, stops after processing N events (for testing)."""
        if not self.inotify.available:
            raise RuntimeError("Linux inotify is unavailable on this system")

        count = self.inotify.add_watch_recursive(self.root_dir)
        self.is_running = True
        events_processed = 0

        try:
            while self.is_running:
                for full_path, mask in self.inotify.read_events(timeout_seconds=0.05):
                    p = Path(full_path)
                    if p.suffix.lower() not in MONITORED_EXTENSIONS:
                        continue

                    # Debounce
                    now = time.time()
                    last_time = self.last_seen_times.get(full_path, 0.0)
                    if (now - last_time) * 1000.0 < self.debounce_ms:
                        continue
                    self.last_seen_times[full_path] = now

                    # Audit
                    res = audit_file(p)
                    self.total_scans += 1
                    events_processed += 1

                    if not res.is_passed:
                        self.total_violations += 1
                        dispatch_reflex_alert(p, "; ".join(res.errors))
                        self.on_violation(res)

                    if max_events is not None and events_processed >= max_events:
                        self.is_running = False
                        break
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        self.inotify.close()
