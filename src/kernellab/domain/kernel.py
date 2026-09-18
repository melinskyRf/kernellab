"""Kernel domain model."""

from __future__ import annotations

from typing import Any


class Kernel:
    """Represents a kernel build or configuration."""

    def __init__(
        self,
        version: str,
        image: str | None = None,
        source: str | None = None,
        config: str | None = None,
        cmdline: str | None = None,
    ) -> None:
        self.version = version
        self.image = image
        self.source = source
        self.config = config
        self.cmdline = cmdline

    def to_dict(self) -> dict[str, Any]:
        """Convert kernel to dictionary."""
        return {
            "version": self.version,
            "image": self.image,
            "source": self.source,
            "config": self.config,
            "cmdline": self.cmdline,
        }

    def __repr__(self) -> str:
        return f"Kernel(version={self.version!r})"
