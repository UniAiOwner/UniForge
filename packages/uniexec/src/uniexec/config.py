"""
UniExec Configuration
=====================
Sandbox boundaries, kernel namespace parameters, and hardware resource limits.
"""

import os
import site
from pathlib import Path

# Resource limits (prlimit / POSIX)
MAX_RAM_BYTES = 536870912  # 512 MB
DEFAULT_TIMEOUT_SECONDS = 15
MAX_TIMEOUT_SECONDS = 60
MAX_PROCESSES = 64
MAX_OPEN_FILES = 64
MAX_FILE_SIZE_BYTES = 10485760  # 10 MB
MAX_OUTPUT_CHARS = 4000

_HOME = Path.home()
_PACKAGES_ROOT = Path(os.environ.get("UNIFORGE_HOME", str(Path(__file__).resolve().parents[3])))
_ENGINE_ROOT = Path(os.environ.get("UNICORTEX_ENGINE_DIR", str(_HOME / ".unicortex" / "engine")))

# Canonical paths for read-only sandbox mounting (only existing paths are bound)
READ_ONLY_MOUNTS = [
    "/usr",
    "/etc",
    str(_HOME / ".agents" / "scripts"),
    str(_HOME / ".agents" / "cortex"),
    str(_HOME / ".unicortex"),
    str(_HOME / ".local"),
    str(_PACKAGES_ROOT),
]

SYSTEM_LIBS = [
    "/lib",
    "/lib64",
    "/bin",
]

SITE_PACKAGES_PATHS = list(dict.fromkeys(site.getsitepackages()))

ENGINE_MODULE_PATHS = [
    str(_ENGINE_ROOT),
    str(_ENGINE_ROOT / "ai_scientist"),
    str(_ENGINE_ROOT / "councils"),
    str(_PACKAGES_ROOT / "unimemory" / "src"),
    str(_PACKAGES_ROOT / "univerify" / "src"),
    str(_PACKAGES_ROOT / "uniexec" / "src"),
]
