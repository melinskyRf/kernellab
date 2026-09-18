"""Runtime-specific exceptions for Kernel Lab."""

from __future__ import annotations

from kernellab.exceptions.base import KernelLabError


class CommandExecutionError(KernelLabError):
    def __init__(
        self,
        command: str,
        exit_code: int,
        stderr: str = "",
    ) -> None:
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        message = f"Command failed with exit code {exit_code}: {command}"
        if stderr:
            message += f"\n{stderr}"
        super().__init__(message)


class CommandTimeoutError(KernelLabError):
    def __init__(self, command: str, timeout: int) -> None:
        self.command = command
        self.timeout = timeout
        super().__init__(f"Command timed out after {timeout}s: {command}")


class RuntimeLockError(KernelLabError):
    def __init__(self, lab_id: str, message: str = "Lock operation failed") -> None:
        self.lab_id = lab_id
        super().__init__(f"{message}: {lab_id}")


class UnsafePathError(KernelLabError):
    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Path traversal detected: {path}")
