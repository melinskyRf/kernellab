"""Job domain model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from kernellab.domain.enums import JobStatus, JobType


class Job:
    """Represents an operation executed on a lab."""

    def __init__(
        self,
        lab_id: str,
        type: JobType,
        id: str | None = None,
        status: JobStatus = JobStatus.PENDING,
        created_at: datetime | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        exit_code: int | None = None,
        error: str | None = None,
        logs: str = "",
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self.lab_id = lab_id
        self.type = type
        self.status = status
        self.created_at = created_at or datetime.now(UTC)
        self.started_at = started_at
        self.finished_at = finished_at
        self.exit_code = exit_code
        self.error = error
        self.logs = logs

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "lab_id": self.lab_id,
            "type": self.type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "exit_code": self.exit_code,
            "error": self.error,
            "logs": self.logs,
        }

    def __repr__(self) -> str:
        return (
            f"Job(id={self.id!r}, lab_id={self.lab_id!r}, "
            f"type={self.type!r}, status={self.status!r})"
        )
