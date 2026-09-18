from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from kernellab.domain.enums import JobStatus, JobType
from kernellab.domain.job import Job
from kernellab.exceptions import JobNotFoundError
from kernellab.logging import get_logger
from kernellab.persistence.repositories import JobRepository  # noqa: TC001

logger = get_logger(__name__)


class JobService:
    def __init__(self, repo: JobRepository) -> None:
        self._repo = repo

    def create_job(self, lab_id: str, job_type: str) -> Job:
        job = Job(lab_id=lab_id, type=JobType(job_type))
        created = self._repo.create(job.to_dict())
        logger.info("Created job %s for lab %s (type=%s)", created.id, lab_id, job_type)
        return created

    def get_job(self, job_id: str) -> Job:
        job = self._repo.get_by_id(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job

    def list_jobs(self, lab_id: str | None = None) -> list[Job]:
        if lab_id is not None:
            return self._repo.get_by_lab_id(lab_id)
        return self._repo.get_all()

    def update_job_status(
        self,
        job_id: str,
        status: str,
        error: str | None = None,
        exit_code: int | None = None,
        logs: str | None = None,
    ) -> Job:
        data: dict[str, Any] = {"status": status}
        if error is not None:
            data["error"] = error
        if exit_code is not None:
            data["exit_code"] = exit_code
        if logs is not None:
            data["logs"] = logs
        if status == JobStatus.RUNNING:
            data["started_at"] = datetime.now(UTC)
        if status in (JobStatus.SUCCESS, JobStatus.FAILED):
            data["finished_at"] = datetime.now(UTC)
        updated = self._repo.update(job_id, data)
        if updated is None:
            raise JobNotFoundError(job_id)
        logger.info("Job %s status -> %s", job_id, status)
        return updated

    def mark_running(self, job_id: str) -> Job:
        return self.update_job_status(job_id, JobStatus.RUNNING)

    def mark_success(self, job_id: str, exit_code: int = 0, logs: str | None = None) -> Job:
        return self.update_job_status(job_id, JobStatus.SUCCESS, exit_code=exit_code, logs=logs)

    def mark_failed(self, job_id: str, error: str, exit_code: int = 1) -> Job:
        return self.update_job_status(job_id, JobStatus.FAILED, error=error, exit_code=exit_code)
