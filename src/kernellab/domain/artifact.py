"""Artifact domain model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


class Artifact:
    """Represents a file or output produced by a job."""

    def __init__(
        self,
        job_id: str,
        name: str,
        path: str,
        artifact_type: str,
        id: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self.job_id = job_id
        self.name = name
        self.path = path
        self.artifact_type = artifact_type
        self.created_at = created_at or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert artifact to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "name": self.name,
            "path": self.path,
            "artifact_type": self.artifact_type,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"Artifact(id={self.id!r}, name={self.name!r}, "
            f"artifact_type={self.artifact_type!r})"
        )
