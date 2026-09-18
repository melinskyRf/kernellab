"""File-based locking for lab runtime operations."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

from kernellab.runtime.exceptions import RuntimeLockError

if TYPE_CHECKING:
    from pathlib import Path


def _pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _read_lock_pid(lock_path: Path) -> int | None:
    try:
        content = lock_path.read_text().strip()
        return int(content)
    except (ValueError, OSError):
        return None


class RuntimeLock:
    """Simple file-based lock per lab."""

    def __init__(self, base_path: Path) -> None:
        self._locks_dir = base_path / "runtime" / "locks"
        self._locks_dir.mkdir(parents=True, exist_ok=True)

    def _lock_path(self, lab_id: str) -> Path:
        return self._locks_dir / f"{lab_id}.lock"

    def acquire(self, lab_id: str, timeout: int = 30) -> bool:
        lock_path = self._lock_path(lab_id)
        deadline = time.monotonic() + timeout

        while True:
            try:
                lock_path.write_text(str(os.getpid()))
                return True
            except FileExistsError:
                pass

            if self._is_stale(lock_path):
                try:
                    lock_path.unlink()
                    lock_path.write_text(str(os.getpid()))
                    return True
                except FileExistsError:
                    pass

            if time.monotonic() >= deadline:
                return False
            time.sleep(0.1)

    def release(self, lab_id: str) -> None:
        lock_path = self._lock_path(lab_id)
        if not lock_path.exists():
            return
        current_pid = os.getpid()
        lock_pid = _read_lock_pid(lock_path)
        if lock_pid == current_pid:
            lock_path.unlink(missing_ok=True)
        else:
            raise RuntimeLockError(
                lab_id,
                message=f"Cannot release lock held by PID {lock_pid}",
            )

    def is_locked(self, lab_id: str) -> bool:
        lock_path = self._lock_path(lab_id)
        if not lock_path.exists():
            return False
        if self._is_stale(lock_path):
            lock_path.unlink(missing_ok=True)
            return False
        return True

    def _is_stale(self, lock_path: Path) -> bool:
        pid = _read_lock_pid(lock_path)
        if pid is None:
            return True
        return not _pid_running(pid)
