from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from kernellab import __version__
from kernellab.cli.config import config_app
from kernellab.cli.doctor import doctor_app
from kernellab.cli.image import image_app
from kernellab.cli.job import job_app
from kernellab.cli.lab import DEFAULT_CONFIG_TEMPLATE, lab_app
from kernellab.cli.output import print_error, print_info, print_success, print_warning
from kernellab.cli.provider import provider_app

console = Console()

app = typer.Typer(
    name="kernellab",
    help="A reproducible laboratory for kernel and driver development.",
    no_args_is_help=True,
)

app.add_typer(lab_app, name="lab")
app.add_typer(job_app, name="job")
app.add_typer(config_app, name="config")
app.add_typer(doctor_app, name="doctor")
app.add_typer(provider_app, name="provider")
app.add_typer(image_app, name="image")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"Kernel Lab {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Kernel Lab CLI."""


@app.command("init")
def init() -> None:
    """Initialize kernellab.yaml and .kernellab/ directory."""
    config_path = Path("kernellab.yaml")
    dot_dir = Path(".kernellab")

    if config_path.exists():
        print_warning(f"'{config_path}' already exists, skipping.")
    else:
        config_path.write_text(DEFAULT_CONFIG_TEMPLATE)
        print_success(f"Created {config_path}")

    if dot_dir.exists():
        print_warning(f"'{dot_dir}/' already exists, skipping.")
    else:
        dot_dir.mkdir(parents=True)
        (dot_dir / "logs").mkdir()
        (dot_dir / "artifacts").mkdir()
        (dot_dir / "runtime").mkdir()
        print_success(f"Created {dot_dir}/ with logs/, artifacts/, runtime/")

    print_info("Project initialized successfully.")


@app.command("logs")
def logs(job_id: str = typer.Argument(..., help="Job ID to show logs for")) -> None:
    """Show logs for a specific job."""
    from kernellab.application.job_service import JobService
    from kernellab.persistence.database import DatabaseManager
    from kernellab.persistence.repositories import JobRepository

    db = DatabaseManager()
    db.create_tables()
    svc = JobService(JobRepository(db))

    try:
        job = svc.get_job(job_id)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    if job.logs:
        from kernellab.cli.output import print_job_logs
        print_job_logs(job.logs)
    else:
        print_info("No logs available for this job.")


@app.command("server")
def server(
    host: str = typer.Option("127.0.0.1", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to listen on"),
) -> None:
    """Start the Kernel Lab API server."""
    import uvicorn

    from kernellab.persistence.database import DatabaseManager

    db = DatabaseManager()
    db.create_tables()
    print_info(f"Starting server on {host}:{port}")
    uvicorn.run("kernellab.api.app:app", host=host, port=port, reload=True)
