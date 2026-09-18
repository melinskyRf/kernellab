from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from kernellab.cli.output import (
    print_error,
    print_job_detail,
    print_job_logs,
    print_table,
)

if TYPE_CHECKING:
    from kernellab.application.job_service import JobService

job_app = typer.Typer(help="Manage jobs")


def _get_services() -> JobService:
    from kernellab.application.job_service import JobService
    from kernellab.persistence.database import DatabaseManager
    from kernellab.persistence.repositories import JobRepository

    db = DatabaseManager()
    db.create_tables()
    repo = JobRepository(db)
    return JobService(repo)


@job_app.command("list")
def list_jobs() -> None:
    """List all jobs."""
    svc = _get_services()
    jobs = svc.list_jobs()

    if not jobs:
        print_error("No jobs found.")
        raise typer.Exit(1)

    rows = [
        [j.id, j.lab_id, j.type.value, j.status.value, j.created_at.strftime("%Y-%m-%d %H:%M:%S")]
        for j in jobs
    ]
    print_table("Jobs", ["ID", "Lab", "Type", "Status", "Created"], rows)


@job_app.command("show")
def show(job_id: str = typer.Argument(..., help="Job ID")) -> None:
    """Show details of a specific job."""
    svc = _get_services()
    try:
        job = svc.get_job(job_id)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    print_job_detail(job.to_dict())

    if job.logs:
        print_job_logs(job.logs)
