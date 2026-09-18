"""Safe external command execution."""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from kernellab.runtime.exceptions import CommandExecutionError, CommandTimeoutError

logger = logging.getLogger(__name__)

_SECRET_PATTERNS = frozenset({"password", "secret", "token", "key"})


@dataclass(frozen=True, slots=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str
    duration: float


@dataclass(frozen=True, slots=True)
class BackgroundProcess:
    pid: int
    executable: str
    args: list[str]


class CommandRunner:
    """Executes external commands safely (never shell=True)."""

    def run(
        self,
        executable: str,
        args: list[str],
        timeout: int = 60,
        check: bool = True,
    ) -> CommandResult:
        cmd = [executable, *args]
        log_line = _safe_log_line(cmd)

        logger.info("Running: %s (timeout=%ds)", log_line, timeout)
        start = time.monotonic()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - start
            logger.warning("Command timed out: %s (%.2fs)", log_line, duration)
            raise CommandTimeoutError(log_line, timeout) from exc
        except FileNotFoundError as exc:
            duration = time.monotonic() - start
            logger.error("Executable not found: %s (%.2fs)", log_line, duration)
            raise CommandExecutionError(
                log_line, exit_code=-1, stderr=str(exc)
            ) from exc

        duration = time.monotonic() - start
        logger.info(
            "Command finished: %s (exit_code=%d, duration=%.2fs)",
            log_line,
            result.returncode,
            duration,
        )

        if check and result.returncode != 0:
            raise CommandExecutionError(
                log_line,
                exit_code=result.returncode,
                stderr=result.stderr,
            )

        return CommandResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=duration,
        )

    def run_background(
        self,
        executable: str,
        args: list[str],
        stdout: int | Path | None = None,
        stderr: int | Path | None = None,
    ) -> BackgroundProcess:
        """Start a process in the background (fire-and-forget)."""
        cmd = [executable, *args]
        log_line = _safe_log_line(cmd)

        logger.info("Starting background: %s", log_line)

        stdout_file = None
        stderr_file = None
        if stdout is not None:
            stdout_file = open(stdout if isinstance(stdout, (str, Path)) else "/dev/null", "w")  # noqa: SIM115
        if stderr is not None:
            stderr_file = open(stderr if isinstance(stderr, (str, Path)) else "/dev/null", "w")  # noqa: SIM115

        try:
            proc = subprocess.Popen(  # noqa: S603
                cmd,
                stdout=stdout_file or subprocess.DEVNULL,
                stderr=stderr_file or subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError as exc:
            raise CommandExecutionError(
                log_line, exit_code=-1, stderr=str(exc)
            ) from exc

        logger.info("Background process started: pid=%d (%s)", proc.pid, log_line)
        return BackgroundProcess(pid=proc.pid, executable=executable, args=args)


def _safe_log_line(cmd: list[str]) -> str:
    parts: list[str] = []
    for token in cmd:
        lower = token.lower()
        if any(p in lower for p in _SECRET_PATTERNS):
            parts.append("***")
        else:
            parts.append(token)
    return " ".join(parts)
