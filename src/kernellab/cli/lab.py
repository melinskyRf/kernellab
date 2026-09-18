from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status
from rich.table import Table

from kernellab.cli.output import (
    print_error,
    print_info,
    print_lab_detail,
    print_success,
    print_table,
    print_warning,
)

lab_app = typer.Typer(help="Manage labs")
console = Console()

DEFAULT_CONFIG_TEMPLATE = """\
version: 1
name: my-lab
description: A reproducible kernel development environment
provider: fake
machine:
  architecture: x86_64
  cpus: 2
  memory: 2G
  disk: 10G
kernel:
  version: "6.12"
workspace:
  source: .
tests:
  - name: boot-test
    command: "echo 'Boot test passed'"
"""


def _get_services():
    from kernellab.application.lab_service import LabService
    from kernellab.persistence.database import DatabaseManager
    from kernellab.persistence.repositories import LabRepository

    db = DatabaseManager()
    db.create_tables()
    repo = LabRepository(db)
    return LabService(repo)


def _get_runtime_services():
    from kernellab.application.job_service import JobService
    from kernellab.application.lab_service import LabService
    from kernellab.application.runtime_service import RuntimeService
    from kernellab.persistence.database import DatabaseManager
    from kernellab.persistence.repositories import JobRepository, LabRepository
    from kernellab.providers.registry import get_provider_registry

    db = DatabaseManager()
    db.create_tables()
    lab_repo = LabRepository(db)
    job_repo = JobRepository(db)
    lab_service = LabService(lab_repo)
    job_service = JobService(job_repo)
    registry = get_provider_registry()
    return lab_service, RuntimeService(job_service, registry), db


@lab_app.command("create")
def create(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Create a new lab."""
    svc = _get_services()
    try:
        lab = svc.create_lab(name)
        print_success(f"Lab '{lab.name}' created (id={lab.id})")
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc


@lab_app.command("list")
def list_labs() -> None:
    """List all labs."""
    svc = _get_services()
    labs = svc.list_labs()

    if not labs:
        print_error("No labs found.")
        raise typer.Exit(1)

    rows = [[lab.id, lab.name, lab.status.value, lab.provider.value] for lab in labs]
    print_table("Labs", ["ID", "Name", "Status", "Provider"], rows)


@lab_app.command("show")
def show(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Show details of a specific lab."""
    svc = _get_services()
    try:
        lab = svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    print_lab_detail(lab.to_dict())


@lab_app.command("delete")
def delete(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Delete a lab."""
    svc = _get_services()
    try:
        lab = svc.get_lab(name=name)
        svc.delete_lab(lab.id)
        print_success(f"Lab '{name}' deleted.")
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc


@lab_app.command("run")
def run(name: str = typer.Argument(..., help="Lab name to run")) -> None:
    """Run a lab from kernellab.yaml."""
    from kernellab.config.loader import load_config

    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    try:
        config = load_config()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    console.print("\n[bold cyan]Kernel Lab[/bold cyan]\n")
    console.print(f"[bold]Lab:[/bold] {name}\n")

    steps = [
        "Environment created",
        "Machine started",
        "Kernel boot simulated",
        "Tests executed",
        "Logs collected",
    ]

    with Status("[dim]Running lab...[/dim]", console=console):
        try:
            job, logs = runtime_svc.run_lab(config, lab.id)
        except Exception as exc:
            print_error(str(exc))
            raise typer.Exit(1) from exc

    for step in steps:
        print_success(step)

    console.print()
    print_success("Job completed successfully.\n")
    console.print(f"[bold]Job ID:[/bold] {job.id}\n")


@lab_app.command("up")
def up(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Create lab if needed, then start it (idempotent)."""
    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception:
        try:
            lab = lab_svc.create_lab(name)
            print_success(f"Lab '{name}' created")
        except Exception as exc:
            print_error(str(exc))
            raise typer.Exit(1) from exc

    if lab.status.value in ("running",):
        print_info(f"Lab '{name}' is already running")
        return

    provider = runtime_svc._registry.get(lab.provider.value)
    config = {"lab_id": lab.id, **lab.configuration}

    with Status(f"[dim]Starting lab '{name}'...[/dim]", console=console):
        try:
            result = provider.start(config)
        except Exception as exc:
            print_error(str(exc))
            raise typer.Exit(1) from exc

    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
        raise typer.Exit(1)


@lab_app.command("start")
def start(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Start a stopped lab."""
    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    provider = runtime_svc._registry.get(lab.provider.value)
    config = {"lab_id": lab.id, **lab.configuration}

    with Status(f"[dim]Starting lab '{name}'...[/dim]", console=console):
        result = provider.start(config)

    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
        raise typer.Exit(1)


@lab_app.command("stop")
def stop(
    name: str = typer.Argument(..., help="Lab name"),
    force: bool = typer.Option(False, "--force", "-f", help="Force stop (poweroff)"),
) -> None:
    """Stop a running lab."""
    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    provider = runtime_svc._registry.get(lab.provider.value)
    config = {"lab_id": lab.id, **lab.configuration}

    with Status(f"[dim]Stopping lab '{name}'...[/dim]", console=console):
        result = provider.stop(config, force=force)

    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
        raise typer.Exit(1)


@lab_app.command("destroy")
def destroy(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Destroy a lab and clean up resources."""
    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    provider = runtime_svc._registry.get(lab.provider.value)
    config = {"lab_id": lab.id, **lab.configuration}

    with Status(f"[dim]Destroying lab '{name}'...[/dim]", console=console):
        result = provider.destroy(config)

    if not result.success:
        print_error(result.message)
        raise typer.Exit(1)

    lab_svc.delete_lab(lab.id)
    print_success(f"Lab '{name}' destroyed and cleaned up")


@lab_app.command("status")
def status_cmd(name: str = typer.Argument(..., help="Lab name")) -> None:
    """Show VM status from provider."""
    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    provider = runtime_svc._registry.get(lab.provider.value)
    config = {"lab_id": lab.id, **lab.configuration}

    result = provider.status(config)

    table = Table(title=f"Lab Status: {name}", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Lab ID", lab.id)
    table.add_row("Name", lab.name)
    table.add_row("Provider", lab.provider.value)
    table.add_row("DB Status", lab.status.value)

    if result.success:
        table.add_row("VM Status", f"[green]{result.message}[/green]")
        for key, val in result.data.items():
            table.add_row(key, str(val))
    else:
        table.add_row("VM Status", f"[red]{result.message}[/red]")

    console.print(table)


@lab_app.command("console")
def console_cmd(
    name: str = typer.Argument(..., help="Lab name"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
) -> None:
    """Show serial log tail."""
    from kernellab.runtime.paths import RuntimePaths

    lab_svc, runtime_svc, db = _get_runtime_services()

    try:
        lab = lab_svc.get_lab(name=name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    paths = RuntimePaths()
    serial_log = paths.serial_log(lab.id)

    if not serial_log.exists():
        print_warning(f"No serial log found for lab '{name}'")
        raise typer.Exit(0)

    try:
        content = serial_log.read_text()
        log_lines = content.splitlines()
        tail = log_lines[-lines:]
        console.print(f"[bold]Serial log for '{name}' (last {len(tail)} lines):[/bold]\n")
        for line in tail:
            console.print(line)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
