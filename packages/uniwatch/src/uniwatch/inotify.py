"""
Native Linux inotify wrapper via ctypes (Zero pip dependencies).
Binds directly to libc.so.6 for sub-millisecond kernel filesystem event delivery.
"""

import os
import struct
import select
import ctypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Generator

from uniwatch.config import IGNORED_DIRECTORIES

# Linux inotify flags
IN_CLOEXEC = 0x00080000
IN_NONBLOCK = 0x00000800
IN_MODIFY = 0x00000002
IN_CLOSE_WRITE = 0x00000008
IN_CREATE = 0x00000100
IN_DELETE = 0x00000200
IN_MOVED_FROM = 0x00000040
IN_MOVED_TO = 0x00000080

DEFAULT_EVENT_MASK = IN_MODIFY | IN_CLOSE_WRITE | IN_CREATE | IN_MOVED_TO

EVENT_HEADER_FMT = "iIII"
EVENT_HEADER_SIZE = struct.calcsize(EVENT_HEADER_FMT)


class NativeInotify:
    """Zero-dependency Linux kernel inotify wrapper using ctypes."""

    def __init__(self):
        self.available = False
        self.fd = -1
        self.watch_descriptors: Dict[int, str] = {}
        self.path_to_wd: Dict[str, int] = {}

        try:
            self.libc = ctypes.CDLL("libc.so.6", use_errno=True)
            self._init1 = self.libc.inotify_init1
            self._init1.argtypes = [ctypes.c_int]
            self._init1.restype = ctypes.c_int

            self._add_watch = self.libc.inotify_add_watch
            self._add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
            self._add_watch.restype = ctypes.c_int

            self._rm_watch = self.libc.inotify_rm_watch
            self._rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
            self._rm_watch.restype = ctypes.c_int

            self.fd = self._init1(IN_NONBLOCK | IN_CLOEXEC)
            if self.fd >= 0:
                self.available = True
        except Exception:
            self.available = False

    def __del__(self):
        self.close()

    def add_watch(self, path: Path, mask: int = DEFAULT_EVENT_MASK) -> int:
        if not self.available or self.fd < 0:
            return -1

        p_str = str(path.resolve())
        if p_str in self.path_to_wd:
            return self.path_to_wd[p_str]

        b_path = p_str.encode("utf-8")
        wd = self._add_watch(self.fd, b_path, mask)
        if wd >= 0:
            self.watch_descriptors[wd] = p_str
            self.path_to_wd[p_str] = wd
        return wd

    def rm_watch(self, wd: int) -> bool:
        if not self.available or self.fd < 0 or wd not in self.watch_descriptors:
            return False

        res = self._rm_watch(self.fd, wd)
        p_str = self.watch_descriptors.pop(wd, None)
        if p_str and p_str in self.path_to_wd:
            del self.path_to_wd[p_str]
        return res == 0

    def add_watch_recursive(self, root: Path, mask: int = DEFAULT_EVENT_MASK) -> int:
        """Recursively registers all non-ignored directories."""
        count = 0
        root_path = root.resolve()
        if not root_path.exists() or not root_path.is_dir():
            return 0

        for current_root, dirs, _ in os.walk(str(root_path), followlinks=False):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES and not d.startswith(".")]

            p = Path(current_root)
            wd = self.add_watch(p, mask=mask)
            if wd >= 0:
                count += 1
        return count

    def read_events(self, timeout_seconds: float = 0.1) -> Generator[Tuple[str, int], None, None]:
        """Reads and yields (full_file_path, mask) for kernel events."""
        if not self.available or self.fd < 0:
            return

        rlist, _, _ = select.select([self.fd], [], [], timeout_seconds)
        if not rlist:
            return

        try:
            raw_data = os.read(self.fd, 65536)
        except (BlockingIOError, OSError):
            return

        offset = 0
        while offset + EVENT_HEADER_SIZE <= len(raw_data):
            wd, mask, cookie, name_len = struct.unpack_from(EVENT_HEADER_FMT, raw_data, offset)
            offset += EVENT_HEADER_SIZE
            if offset + name_len > len(raw_data):
                break

            name = ""
            if name_len > 0:
                name_bytes = raw_data[offset:offset + name_len]
                offset += name_len
                name = name_bytes.rstrip(b"\x00").decode("utf-8", errors="replace")

            parent_dir = self.watch_descriptors.get(wd)
            if parent_dir:
                full_path = os.path.join(parent_dir, name) if name else parent_dir
                yield full_path, mask

    def close(self):
        if self.fd >= 0:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = -1
        self.watch_descriptors.clear()
        self.path_to_wd.clear()
        self.available = False
