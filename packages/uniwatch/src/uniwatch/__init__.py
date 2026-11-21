"""
UniWatch: Sovereign Filesystem Inotify Compiler & Syntax Watchdog.
"""

from uniwatch.engine import UniWatchEngine
from uniwatch.watcher import WatcherLoop, audit_file, FileWatchAuditResult
from uniwatch.inotify import NativeInotify
from uniwatch.parsers import validate_file_syntax

__version__ = "2026.1.0"
__all__ = [
    "UniWatchEngine",
    "WatcherLoop",
    "audit_file",
    "FileWatchAuditResult",
    "NativeInotify",
    "validate_file_syntax",
]
