"""Dependency injection for Kernel Lab API."""

from __future__ import annotations

from collections.abc import Generator  # noqa: TC003
from typing import Annotated

from fastapi import Depends

from kernellab.application.job_service import JobService
from kernellab.application.lab_service import LabService
from kernellab.application.runtime_service import RuntimeService
from kernellab.persistence.database import DatabaseManager
from kernellab.persistence.repositories import JobRepository, LabRepository
from kernellab.providers.registry import get_provider_registry


def get_database_manager() -> Generator[DatabaseManager, None, None]:
    """Yield a DatabaseManager instance."""
    db = DatabaseManager()
    try:
        yield db
    finally:
        pass  # DatabaseManager doesn't require explicit cleanup


def get_lab_service(
    db: Annotated[DatabaseManager, Depends(get_database_manager)],
) -> LabService:
    """Create a LabService with dependency injection."""
    repo = LabRepository(db)
    return LabService(repo)


def get_job_service(
    db: Annotated[DatabaseManager, Depends(get_database_manager)],
) -> JobService:
    """Create a JobService with dependency injection."""
    repo = JobRepository(db)
    return JobService(repo)


def get_runtime_service(
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> RuntimeService:
    """Create a RuntimeService with dependency injection."""
    registry = get_provider_registry()
    return RuntimeService(job_service, registry)
