"""
UniMemory Configuration
=======================
Governs storage paths, WAL pragmas, and memory limits.
"""

import os
from pathlib import Path

# Base Paths
DEFAULT_UNICORTEX_DIR = Path(os.environ.get("UNICORTEX_HOME", str(Path.home() / ".unicortex")))
DEFAULT_DB_PATH = DEFAULT_UNICORTEX_DIR / "brain_memory.db"

BRAIN_MEMORY_DB = Path(os.environ.get("UNICORTEX_BRAIN_MEMORY_DB", str(DEFAULT_DB_PATH)))

# SQLite WAL Pragmas
PRAGMAS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "temp_store": "MEMORY",
    "cache_size": "-64000",       # 64 MB in-memory page cache
    "busy_timeout": "5000",       # 5.0s busy timeout
    "foreign_keys": "ON"
}

# Retrieval Bounds
DEFAULT_TOP_K = 5
MAX_WORKING_ITEMS = 50
WORKING_MEMORY_TTL_HOURS = 24
BM25_THRESHOLD = -2.5
