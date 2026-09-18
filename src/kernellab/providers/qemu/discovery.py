from __future__ import annotations

import logging
import platform
import shutil
from dataclasses import dataclass

from kernellab.runtime.command_runner import CommandRunner

logger = logging.getLogger(__name__)

_QEMU_SYSTEM_EXECUTABLES = [
    "qemu-system-x86_64",
    "qemu-system-i386",
]

_QEMU_IMG_EXECUTABLE = "qemu-img"


@dataclass
class DiscoveryResult:
    available: bool
    system_executable: str
    img_executable: str
    version: str
    acceleration: str


def detect() -> DiscoveryResult:
    system_executable = _find_system_executable()
    img_executable = shutil.which(_QEMU_IMG_EXECUTABLE) or ""

    if not system_executable:
        return DiscoveryResult(
            available=False,
            system_executable="",
            img_executable=img_executable,
            version="",
            acceleration="",
        )

    version = _get_version(system_executable)
    acceleration = _detect_acceleration()

    return DiscoveryResult(
        available=True,
        system_executable=system_executable,
        img_executable=img_executable,
        version=version,
        acceleration=acceleration,
    )


def _find_system_executable() -> str:
    for exe in _QEMU_SYSTEM_EXECUTABLES:
        found = shutil.which(exe)
        if found:
            return found
    return ""


def _get_version(executable: str) -> str:
    runner = CommandRunner()
    try:
        result = runner.run(executable, ["--version"], timeout=10, check=False)
        return result.stdout.strip()
    except Exception:
        logger.warning("Failed to get QEMU version", exc_info=True)
        return ""


def _detect_acceleration() -> str:
    system = platform.system()

    if system == "Linux":
        if shutil.which("kvm"):
            return "kvm"
        import os

        if os.path.exists("/dev/kvm"):
            return "kvm"
        return "tcg"

    if system == "Windows":
        if shutil.which("whpx"):
            return "whpx"
        return "tcg"

    if system == "Darwin":
        if shutil.which("hvf"):
            return "hvf"
        return "tcg"

    return "tcg"
