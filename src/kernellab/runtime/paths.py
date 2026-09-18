"""Path management for lab runtime directories."""

from __future__ import annotations

from pathlib import Path

from kernellab.runtime.exceptions import UnsafePathError

# Allowlist of safe characters for lab_id (alphanumeric, hyphens, underscores)
_SAFE_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")


def _validate_lab_id(lab_id: str) -> str:
    if not lab_id:
        raise UnsafePathError("(empty lab_id)")
    if any(c not in _SAFE_ID_CHARS for c in lab_id):
        raise UnsafePathError(lab_id)
    if ".." in lab_id:
        raise UnsafePathError(lab_id)
    return lab_id


class RuntimePaths:
    """Manages paths for lab runtime directories."""

    def __init__(self, base_path: str | Path = ".kernellab") -> None:
        self._base = Path(base_path)

    @property
    def base(self) -> Path:
        return self._base

    def lab_dir(self, lab_id: str) -> Path:
        _validate_lab_id(lab_id)
        return self._base / "labs" / lab_id

    def runtime_json(self, lab_id: str) -> Path:
        return self.lab_dir(lab_id) / "runtime.json"

    def serial_log(self, lab_id: str) -> Path:
        return self.lab_dir(lab_id) / "serial.log"

    def vm_dir(self, lab_id: str) -> Path:
        return self.lab_dir(lab_id) / "vm"

    def artifacts_dir(self, lab_id: str) -> Path:
        return self.lab_dir(lab_id) / "artifacts"

    def images_dir(self) -> Path:
        return self._base / "images"

    def locks_dir(self) -> Path:
        return self._base / "runtime" / "locks"

    def logs_dir(self) -> Path:
        return self._base / "logs"

    def ensure_lab_dirs(self, lab_id: str) -> None:
        dirs = [
            self.lab_dir(lab_id),
            self.vm_dir(lab_id),
            self.artifacts_dir(lab_id),
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
