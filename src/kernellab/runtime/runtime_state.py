"""Runtime state model for machines."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class MachineRuntime:
    """Tracks runtime state of a virtual machine."""

    id: str
    lab_id: str
    provider: str
    provider_machine_id: str
    provider_machine_name: str
    state: str
    runtime_path: str
    serial_log: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "lab_id": self.lab_id,
            "provider": self.provider,
            "provider_machine_id": self.provider_machine_id,
            "provider_machine_name": self.provider_machine_name,
            "state": self.state,
            "runtime_path": self.runtime_path,
            "serial_log": self.serial_log,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MachineRuntime:
        return cls(
            id=data["id"],
            lab_id=data["lab_id"],
            provider=data["provider"],
            provider_machine_id=data["provider_machine_id"],
            provider_machine_name=data["provider_machine_name"],
            state=data["state"],
            runtime_path=data["runtime_path"],
            serial_log=data["serial_log"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )
