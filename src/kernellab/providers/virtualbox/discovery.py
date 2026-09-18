from __future__ import annotations

import logging
import platform
import shutil
from dataclasses import dataclass

from kernellab.runtime.command_runner import CommandRunner

logger = logging.getLogger(__name__)

_WINDOWS_VBOX_PATHS = [
    r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
]


@dataclass
class DiscoveryResult:
    available: bool
    executable: str
    version: str
    host_info: str = ""


def detect() -> DiscoveryResult:
    executable = _find_executable()
    if not executable:
        return DiscoveryResult(available=False, executable="", version="", host_info="")

    version = _get_version(executable)
    host_info = platform.platform()

    return DiscoveryResult(
        available=True,
        executable=executable,
        version=version,
        host_info=host_info,
    )


def _find_executable() -> str:
    found = shutil.which("VBoxManage")
    if found:
        return found

    if platform.system() == "Windows":
        for path in _WINDOWS_VBOX_PATHS:
            if shutil.which(path):
                return path

    return ""


def _get_version(executable: str) -> str:
    runner = CommandRunner()
    try:
        result = runner.run(executable, ["--version"], timeout=10, check=False)
        return result.stdout.strip()
    except Exception:
        logger.warning("Failed to get VBoxManage version", exc_info=True)
        return ""
