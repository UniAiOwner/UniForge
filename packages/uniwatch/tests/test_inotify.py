"""
Tests for UniWatch Native Inotify Wrapper.
"""

from pathlib import Path
from uniwatch.inotify import NativeInotify


def test_native_inotify_lifecycle(tmp_path: Path):
    inotify = NativeInotify()
    assert inotify.available is True
    assert inotify.fd >= 0

    # Add watch
    sub_dir = tmp_path / "src"
    sub_dir.mkdir()
    wd = inotify.add_watch(sub_dir)
    assert wd >= 0

    # Trigger filesystem event
    test_file = sub_dir / "test.py"
    test_file.write_text("x = 1\n")

    # Read events
    events = list(inotify.read_events(timeout_seconds=0.2))
    assert len(events) >= 1
    paths = [p for p, _ in events]
    assert any("test.py" in p for p in paths)

    # Cleanup
    inotify.close()
    assert inotify.fd == -1
