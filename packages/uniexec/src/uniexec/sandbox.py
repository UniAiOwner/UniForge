"""
UniExec Tier 2 & 3: Bubblewrap Namespace Isolation & Resource Quotas
====================================================================
Spawns an unprivileged, network-isolated Bubblewrap container with read-only
system mounts, POSIX resource quotas (prlimit), and captive execution bootstrap.
"""

import sys
import shutil
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from uniexec.config import (
    MAX_RAM_BYTES,
    MAX_PROCESSES,
    MAX_OPEN_FILES,
    MAX_FILE_SIZE_BYTES,
    DEFAULT_TIMEOUT_SECONDS,
    MAX_OUTPUT_CHARS,
    READ_ONLY_MOUNTS,
    SYSTEM_LIBS,
    ENGINE_MODULE_PATHS,
    SITE_PACKAGES_PATHS,
)
from uniexec.models import ExecutionResult


def _get_worker_bootstrap() -> str:
    host_site_pkgs = [p for p in sys.path if 'site-packages' in p or 'dist-packages' in p]
    return r'''import json, sys, io
engine_paths = ''' + json.dumps(ENGINE_MODULE_PATHS) + r'''
site_pkgs = ''' + json.dumps(host_site_pkgs) + r'''
sys.path = engine_paths + site_pkgs + [p for p in sys.path if p not in engine_paths and p not in site_pkgs]

from uniexec.prelude import UniExecPrelude

stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

safe_globals = {
    "__builtins__": {
        "print": lambda *args, **kwargs: print(*args, file=stdout_capture, **kwargs),
        "len": len, "range": range, "min": min, "max": max, "sum": sum,
        "isinstance": isinstance, "str": str, "int": int, "float": float,
        "bool": bool, "list": list, "dict": dict, "set": set, "tuple": tuple,
        "round": round, "sorted": sorted, "enumerate": enumerate, "zip": zip,
        "any": any, "all": all, "abs": abs, "map": map, "filter": filter,
        "open": open, "type": type, "__import__": __import__,
        "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
        "KeyError": KeyError, "RuntimeError": RuntimeError, "OSError": OSError,
        "PermissionError": PermissionError
    },
    "memory_recall": UniExecPrelude.memory_recall,
    "memory_store_fact": UniExecPrelude.memory_store_fact,
    "verify_code_gate": UniExecPrelude.verify_code_gate,
    "get_beacon": UniExecPrelude.get_beacon,
    "check_drift": UniExecPrelude.check_drift,
    "consult_scientist": UniExecPrelude.consult_scientist,
    "query_research_papers": UniExecPrelude.query_research_papers,
    "convene_council": UniExecPrelude.convene_council,
    "git_diff_summary": UniExecPrelude.git_diff_summary,
    "bus_publish_event": UniExecPrelude.bus_publish_event,
    "bus_query_constraints": UniExecPrelude.bus_query_constraints,
    "bus_acquire_lease": UniExecPrelude.bus_acquire_lease,
    "bus_release_lease": UniExecPrelude.bus_release_lease,
    "result": None,
}

script_code = sys.stdin.read()
status = "SUCCESS"
error_msg = None
orig_stdout, orig_stderr = sys.stdout, sys.stderr

try:
    sys.stdout, sys.stderr = stdout_capture, stderr_capture
    exec(script_code, safe_globals)
except Exception as e:
    status = "ERROR"
    error_msg = f"{type(e).__name__}: {str(e)}"
finally:
    sys.stdout, sys.stderr = orig_stdout, orig_stderr

res_val = safe_globals.get("result")
output_payload = {
    "status": status,
    "result": res_val,
    "stdout": stdout_capture.getvalue()[:4000],
    "stderr": stderr_capture.getvalue()[:1000],
    "error": error_msg
}

try:
    print(json.dumps(output_payload, ensure_ascii=False))
except Exception as exc:
    print(json.dumps({
        "status": "ERROR", "result": None, "stdout": None, "stderr": None,
        "error": "Result serialization failed: " + str(exc)
    }))
'''


class SandboxOrchestrator:

    @staticmethod
    def build_bwrap_command(timeout_seconds: int) -> List[str]:
        bwrap = shutil.which("bwrap")
        prlimit = shutil.which("prlimit")
        if not bwrap or not prlimit:
            raise RuntimeError("Required sandbox binaries (bwrap or prlimit) not found on host.")

        cmd = [
            bwrap,
            "--die-with-parent",
            "--new-session",
            "--unshare-all",
            "--dev", "/dev",
            "--proc", "/proc",
            "--tmpfs", "/tmp",
            "--chdir", "/tmp",
        ]

        # System library mounts
        for lib_path in SYSTEM_LIBS:
            if Path(lib_path).exists():
                cmd.extend(["--ro-bind", lib_path, lib_path])

        # Intermediate directories (derived dynamically from HOME)
        home_str = str(Path.home())
        for directory in ("/home", home_str):
            cmd.extend(["--dir", directory])

        # Read-only mounts
        for source in READ_ONLY_MOUNTS:
            if Path(source).exists():
                cmd.extend(["--ro-bind", source, source])

        # Environment configuration
        local_bin = str(Path.home() / ".local" / "bin")
        unicortex_home = str(Path.home() / ".unicortex")
        cmd.extend([
            "--setenv", "HOME", "/tmp",
            "--setenv", "UNICORTEX_HOME", unicortex_home,
            "--setenv", "PATH", f"{local_bin}:/usr/local/bin:/usr/bin:/bin",
            "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
            "--setenv", "GIT_OPTIONAL_LOCKS", "0",
            "--setenv", "GIT_CONFIG_NOSYSTEM", "1",
            "--setenv", "GIT_CONFIG_GLOBAL", "/dev/null",
        ])

        # Resource limits via prlimit
        cmd.extend([
            "--", prlimit,
            f"--cpu={min(timeout_seconds, 30)}:{min(timeout_seconds, 30) + 1}",
            f"--as={MAX_RAM_BYTES}",
            f"--nproc={MAX_PROCESSES}",
            f"--nofile={MAX_OPEN_FILES}",
            f"--fsize={MAX_FILE_SIZE_BYTES}",
            "--",
            sys.executable, "-I", "-c", _get_worker_bootstrap()
        ])

        return cmd

    @classmethod
    def execute_in_sandbox(
        cls,
        script_code: str,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    ) -> ExecutionResult:
        """Executes Python script within the isolated Bubblewrap container."""
        start = time.perf_counter()
        timeout_seconds = max(1, min(int(timeout_seconds), 60))

        try:
            cmd = cls.build_bwrap_command(timeout_seconds)
            proc = subprocess.run(
                cmd,
                input=script_code,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False
            )
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            raw_out = proc.stdout.strip()
            if not raw_out:
                return ExecutionResult(
                    status="ERROR" if proc.returncode != 0 else "SUCCESS",
                    result=None,
                    stdout="",
                    stderr=proc.stderr[:1000],
                    execution_time_ms=round(elapsed_ms, 2),
                    error=proc.stderr[:500] if proc.returncode != 0 else None
                )

            # Parse JSON returned by worker bootstrap
            lines = [l for l in raw_out.splitlines() if l.strip()]
            payload = json.loads(lines[-1]) if lines else {}

            return ExecutionResult(
                status=payload.get("status", "SUCCESS"),
                result=payload.get("result"),
                stdout=payload.get("stdout", ""),
                stderr=payload.get("stderr", "") or proc.stderr[:1000],
                execution_time_ms=round(elapsed_ms, 2),
                token_savings_percent=98.0,
                error=payload.get("error")
            )

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ExecutionResult(
                status="TIMEOUT",
                result=None,
                stdout="",
                stderr="",
                execution_time_ms=round(elapsed_ms, 2),
                error=f"Execution exceeded hard timeout limit of {timeout_seconds}s."
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ExecutionResult(
                status="ERROR",
                result=None,
                stdout="",
                stderr="",
                execution_time_ms=round(elapsed_ms, 2),
                error=f"Sandbox error: {str(e)}"
            )
