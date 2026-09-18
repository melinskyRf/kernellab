"""Job endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from kernellab.api.dependencies import get_job_service
from kernellab.application.job_service import JobService  # noqa: TC001
from kernellab.exceptions import JobNotFoundError, KernelLabError
from kernellab.schemas.job import JobListResponse, JobLogsResponse, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    job_service: Annotated[JobService, Depends(get_job_service)],
    lab_id: str | None = Query(None, description="Filter jobs by lab ID"),
) -> JobListResponse:
    """List jobs, optionally filtered by lab ID."""
    try:
        jobs = job_service.list_jobs(lab_id=lab_id)
        items = [JobResponse.model_validate(job) for job in jobs]
        return JobListResponse(items=items, total=len(items))
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> JobResponse:
    """Get a job by ID."""
    try:
        job = job_service.get_job(job_id)
        return JobResponse.model_validate(job)
    except JobNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.get("/{job_id}/logs", response_model=JobLogsResponse)
async def get_job_logs(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> JobLogsResponse:
    """Get logs for a job."""
    try:
        job = job_service.get_job(job_id)

        log_path = Path(f".kernellab/logs/{job_id}.log")
        logs = log_path.read_text() if log_path.exists() else job.logs

        return JobLogsResponse(job_id=job_id, logs=logs)
    except JobNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None
