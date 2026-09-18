"""Image domain model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


class Image:
    """Represents a virtual machine image."""

    def __init__(
        self,
        name: str,
        provider: str,
        format: str,
        path: str,
        architecture: str = "x86_64",
        id: str | None = None,
        created_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.provider = provider
        self.format = format
        self.path = path
        self.architecture = architecture
        self.created_at = created_at or datetime.now(UTC)
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert image to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "format": self.format,
            "path": self.path,
            "architecture": self.architecture,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"Image(id={self.id!r}, name={self.name!r}, provider={self.provider!r})"
