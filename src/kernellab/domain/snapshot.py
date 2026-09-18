"""Snapshot domain model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


class Snapshot:
    """Represents a saved state of a lab environment."""

    def __init__(
        self,
        lab_id: str,
        name: str,
        description: str | None = None,
        id: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self.lab_id = lab_id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "id": self.id,
            "lab_id": self.lab_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"Snapshot(id={self.id!r}, lab_id={self.lab_id!r}, "
            f"name={self.name!r})"
        )
