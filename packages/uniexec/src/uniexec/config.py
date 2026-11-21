"""
UniExec Configuration
=====================
Sandbox boundaries, kernel namespace parameters, and hardware resource limits.
"""

from pathlib import Path

# Resource limits (prlimit / POSIX)
MAX_RAM_BYTES = 536870912  # 512 MB
DEFAULT_TIMEOUT_SECONDS = 15
MAX_TIMEOUT_SECONDS = 60
MAX_PROCESSES = 64
MAX_OPEN_FILES = 64
MAX_FILE_SIZE_BYTES = 10485760  # 10 MB
MAX_OUTPUT_CHARS = 4000

# Canonical paths for read-only sandbox mounting
READ_ONLY_MOUNTS = [
    "/usr",
    "/etc",
    "/home/uniai/.agents/scripts",
    "/home/uniai/.agents/cortex",
    "/home/uniai/.unicortex",
    "/home/uniai/.local",
    "/media/uniai/UniAi/PROJECTS_MIGRATED",
]

SYSTEM_LIBS = [
    "/lib",
    "/lib64",
    "/bin"
]

SITE_PACKAGES_PATHS = [
    "/home/uniai/.local/lib/python3.12/site-packages",
    "/home/uniai/.local/share/uv/python/cpython-3.14.10-linux-x86_64-gnu/lib/python3.14/site-packages"
]

ENGINE_MODULE_PATHS = [
    "/media/uniai/UniAi/PROJECTS_MIGRATED/Agentic team/01_UNICORTEX_ENGINE",
    "/media/uniai/UniAi/PROJECTS_MIGRATED/Agentic team/01_UNICORTEX_ENGINE/ai_scientist",
    "/media/uniai/UniAi/PROJECTS_MIGRATED/Agentic team/01_UNICORTEX_ENGINE/councils",
    "/media/uniai/UniAi/PROJECTS_MIGRATED/unimemory/src",
    "/media/uniai/UniAi/PROJECTS_MIGRATED/univerify/src",
    "/media/uniai/UniAi/PROJECTS_MIGRATED/uniexec/src"
]
