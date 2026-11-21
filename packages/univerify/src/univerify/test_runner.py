"""
UniVerify Level 4: Test Harness Runner
======================================
Executes real empirical test suites (pytest, cargo, gradlew) and parses output
to guarantee zero simulated passes and zero fake tests (Constitutional Law-000).
"""

import subprocess
import time
import re
from pathlib import Path
from typing import List, Optional
from univerify.models import TestRunResult


class TestRunner:
    """
    Executes tests deterministically in the local host environment.
    """

    @staticmethod
    def run_command(
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout_sec: int = 120
    ) -> TestRunResult:
        """Runs an arbitrary test command and packages the empirical result."""
        start = time.perf_counter()
        cmd_str = " ".join(cmd)
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            duration = time.perf_counter() - start
            stdout = res.stdout or ""
            stderr = res.stderr or ""
            combined = stdout + "\n" + stderr

            passed = (res.returncode == 0)
            failures = []
            if not passed:
                # Capture first 10 failure lines
                for line in combined.splitlines():
                    if any(term in line.lower() for term in ["fail", "error", "exception", "assert"]):
                        failures.append(line.strip())
                        if len(failures) >= 10:
                            break

            return TestRunResult(
                command=cmd_str,
                exit_code=res.returncode,
                passed=passed,
                duration_sec=round(duration, 3),
                output_summary=combined[-1000:],
                failures=failures
            )
        except subprocess.TimeoutExpired:
            duration = time.perf_counter() - start
            return TestRunResult(
                command=cmd_str,
                exit_code=124,
                passed=False,
                duration_sec=round(duration, 3),
                output_summary=f"Execution timed out after {timeout_sec} seconds.",
                failures=[f"TIMEOUT: Command exceeded {timeout_sec}s threshold."]
            )
        except Exception as e:
            duration = time.perf_counter() - start
            return TestRunResult(
                command=cmd_str,
                exit_code=1,
                passed=False,
                duration_sec=round(duration, 3),
                output_summary=str(e),
                failures=[f"EXECUTION_ERROR: {str(e)}"]
            )

    @classmethod
    def run_pytest(
        cls,
        test_path: str,
        cwd: Optional[str] = None,
        timeout_sec: int = 60
    ) -> TestRunResult:
        """Executes pytest and parses test counts and failures."""
        cmd = ["pytest", "-v", test_path]
        result = cls.run_command(cmd, cwd=cwd, timeout_sec=timeout_sec)

        # Parse pytest output
        # e.g.: "==== 13 passed in 0.42s ====" or "==== 2 failed, 11 passed in 1.20s ===="
        output = result.output_summary
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)

        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0

        result.passed_tests = passed_count
        result.failed_tests = failed_count
        result.total_tests = passed_count + failed_count

        return result
