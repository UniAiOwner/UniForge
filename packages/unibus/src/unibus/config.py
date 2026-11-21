"""
UniBus Configuration & Canonical Paths.
"""

import os
from pathlib import Path

# Paths
DEFAULT_TMP_SOCKET = Path("/tmp/unibus.sock")
USER_RUNTIME_DIR = Path(f"/run/user/{os.getuid()}") if hasattr(os, "getuid") else None
USER_SOCKET = USER_RUNTIME_DIR / "unibus.sock" if USER_RUNTIME_DIR and USER_RUNTIME_DIR.exists() else None

# Canonical Socket Path (Prefer user runtime dir if available for permission isolation, else /tmp)
CANONICAL_SOCKET_PATH = USER_SOCKET if USER_SOCKET else DEFAULT_TMP_SOCKET

# Canonical DB Path (SQLite WAL)
CANONICAL_DB_DIR = Path.home() / ".unicortex"
CANONICAL_DB_PATH = CANONICAL_DB_DIR / "unibus.db"

# Lease Defaults
DEFAULT_LEASE_TTL_SECONDS = 60
MAX_LEASE_TTL_SECONDS = 3600

# Event Defaults
MAX_EVENT_BYTES = 1_048_576  # 1 MB
DEFAULT_EVENT_POLL_LIMIT = 50

# Heartbeat Defaults
STALE_HEARTBEAT_THRESHOLD_SECONDS = 60
