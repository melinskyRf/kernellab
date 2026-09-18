from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.table import Table

from kernellab.cli.output import print_error, print_info, print_success

doctor_app = typer.Typer(help="Check system health and dependencies")
console = Console()


def _check_python_version() -> tuple[str, str, str]:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return ("Python", "OK", f"{version} ({sys.executable})")


def _check_kernellab_version() -> tuple[str, str, str]:
    from kernellab import __version__
    return ("Kernel Lab", "OK", f"v{__version__}")


def _check_database() -> tuple[str, str, str]:
    from pathlib import Path

    db_path = Path(".kernellab/kernellab.db")
    if not db_path.exists():
        return ("Database", "WARN", ".kernellab/kernellab.db not found (run 'kernellab init')")
    try:
        from kernellab.persistence.database import DatabaseManager
        db = DatabaseManager()
        db.create_tables()
        return ("Database", "OK", f"{db_path} ({db_path.stat().st_size} bytes)")
    except Exception as exc:
        return ("Database", "ERROR", str(exc))


def _check_virtualbox() -> tuple[str, str, str]:
    try:
        from kernellab.providers.virtualbox.discovery import detect
        result = detect()
        if result.available:
            return ("VirtualBox", "OK", f"{result.executable} ({result.version})")
        return ("VirtualBox", "SKIP", "not installed")
    except Exception as exc:
        return ("VirtualBox", "ERROR", str(exc))


def _check_qemu() -> tuple[str, str, str]:
    try:
        from kernellab.providers.qemu.discovery import detect
        result = detect()
        if result.available:
            detail = f"{result.system_executable} ({result.version})"
            if result.acceleration:
                detail += f" [{result.acceleration}]"
            return ("QEMU", "OK", detail)
        return ("QEMU", "SKIP", "not installed")
    except Exception as exc:
        return ("QEMU", "ERROR", str(exc))


def _check_kvm() -> tuple[str, str, str]:
    import os
    import platform

    system = platform.system()
    if system == "Linux":
        if os.path.exists("/dev/kvm"):
            return ("KVM", "OK", "/dev/kvm present")
        return ("KVM", "WARN", "/dev/kvm not found (acceleration may be limited)")
    return ("KVM", "SKIP", f"not applicable on {system}")


_CHECKS = [
    _check_python_version,
    _check_kernellab_version,
    _check_database,
    _check_virtualbox,
    _check_qemu,
    _check_kvm,
]

STATUS_STYLES = {
    "OK": "green",
    "WARN": "yellow",
    "ERROR": "red",
    "SKIP": "dim",
}


@doctor_app.command("doctor")
def doctor() -> None:
    """Check system health and dependencies."""
    table = Table(title="System Health", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Details")

    results = [check() for check in _CHECKS]

    for component, status, details in results:
        style = STATUS_STYLES.get(status, "white")
        table.add_row(component, f"[{style}]{status}[/{style}]", details)

    console.print(table)

    errors = sum(1 for _, s, _ in results if s == "ERROR")
    warnings = sum(1 for _, s, _ in results if s == "WARN")

    if errors:
        print_error(f"{errors} error(s) found")
        raise typer.Exit(1)
    elif warnings:
        print_info(f"{warnings} warning(s) found")
    else:
        print_success("All checks passed")
