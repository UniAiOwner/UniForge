"""
UniWatch Engine Facade.
"""

from pathlib import Path
from typing import Dict, Any, List

from uniwatch.config import INOTIFY_MAX_USER_WATCHES_PATH
from uniwatch.inotify import NativeInotify
from uniwatch.watcher import audit_file, FileWatchAuditResult


class UniWatchEngine:
    """Master UniWatch engine providing pre-flight audits and diagnostics."""

    @staticmethod
    def check_file(file_path: Path) -> FileWatchAuditResult:
        return audit_file(Path(file_path))

    @staticmethod
    def check_tree(root_dir: Path) -> List[FileWatchAuditResult]:
        results: List[FileWatchAuditResult] = []
        p = Path(root_dir)
        if p.is_file():
            return [audit_file(p)]

        for item in p.rglob("*"):
            if item.is_file() and not any(part.startswith(".") for part in item.parts):
                res = audit_file(item)
                if not res.is_passed or res.warnings:
                    results.append(res)
        return results

    @staticmethod
    def doctor() -> Dict[str, Any]:
        inotify = NativeInotify()
        inotify_ok = inotify.available
        inotify.close()

        max_watches = 0
        if INOTIFY_MAX_USER_WATCHES_PATH.exists():
            try:
                max_watches = int(INOTIFY_MAX_USER_WATCHES_PATH.read_text().strip())
            except Exception:
                pass

        return {
            "status": "HEALTHY" if inotify_ok and max_watches > 8192 else "DEGRADED",
            "inotify_available": inotify_ok,
            "max_user_watches": max_watches,
            "kernel_capacity_sufficient": max_watches >= 65536,
        }

    @staticmethod
    def status() -> Dict[str, Any]:
        doc = UniWatchEngine.doctor()
        return {
            "inotify_available": doc["inotify_available"],
            "max_user_watches": doc["max_user_watches"],
            "status": doc["status"],
        }
