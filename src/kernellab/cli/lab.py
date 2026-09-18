from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from kernellab.cli.output import (
    print_error,
    print_lab_detail,
    print_success,
    print_table,
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
