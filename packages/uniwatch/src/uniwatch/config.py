"""
UniWatch Configuration & Invariants.
"""

from pathlib import Path
from typing import Set

# Monitored Extensions
MONITORED_EXTENSIONS: Set[str] = {
    ".py",
    ".kt",
    ".kts",
    ".rs",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".sql",
}

# Directories Ignored from Recursive Watch
IGNORED_DIRECTORIES: Set[str] = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "build",
    ".gradle",
    "dist",
    ".venv",
    ".idea",
    ".unigov",
}

# Timing & Limits
DEFAULT_DEBOUNCE_MS = 50
MAX_SCAN_BYTES = 5 * 1024 * 1024  # 5 MB
INOTIFY_MAX_USER_WATCHES_PATH = Path("/proc/sys/fs/inotify/max_user_watches")
