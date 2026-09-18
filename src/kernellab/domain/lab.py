"""Lab domain model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from kernellab.domain.enums import LabStatus, ProviderType


class Lab:
    """Represents a kernel development/testing environment."""

    def __init__(
        self,
        name: str,
        provider: ProviderType = ProviderType.FAKE,
        description: str | None = None,
        configuration: dict[str, Any] | None = None,
        id: str | None = None,
        status: LabStatus = LabStatus.CREATED,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.provider = provider
        self.status = status
        self.configuration = configuration or {}
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert lab to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "provider": self.provider.value,
            "status": self.status.value,
            "configuration": self.configuration,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"Lab(id={self.id!r}, name={self.name!r}, status={self.status!r})"
