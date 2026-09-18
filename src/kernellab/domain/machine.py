"""Machine domain model."""

from __future__ import annotations

from typing import Any

from kernellab.domain.enums import Architecture


class Machine:
    """Represents a virtual machine configuration."""

    def __init__(
        self,
        architecture: Architecture = Architecture.X86_64,
        cpus: int = 2,
        memory: str = "2G",
        disk: str = "10G",
    ) -> None:
        self.architecture = architecture
        self.cpus = cpus
        self.memory = memory
        self.disk = disk

    def to_dict(self) -> dict[str, Any]:
        """Convert machine to dictionary."""
        return {
            "architecture": self.architecture.value,
            "cpus": self.cpus,
            "memory": self.memory,
            "disk": self.disk,
        }

    def __repr__(self) -> str:
        return (
            f"Machine(architecture={self.architecture!r}, cpus={self.cpus!r}, "
            f"memory={self.memory!r}, disk={self.disk!r})"
        )
