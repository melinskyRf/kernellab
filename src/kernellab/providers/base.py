from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)


@dataclass
class ProviderInfo:
    available: bool
    version: str
    executable: str
    host_info: str = ""


@dataclass
class ProviderCapabilities:
    create: bool = True
    start: bool = True
    stop: bool = True
    destroy: bool = True
    serial: bool = False
    snapshots: bool = False
    guest_exec: bool = False
    all: bool = False

    def __post_init__(self) -> None:
        self.all = (
            self.create
            and self.start
            and self.stop
            and self.destroy
            and self.serial
            and self.snapshots
            and self.guest_exec
        )


class Provider(ABC):
    @abstractmethod
    def create(self, config: dict[str, Any]) -> ProviderResult: ...

    @abstractmethod
    def start(self, config: dict[str, Any]) -> ProviderResult: ...

    @abstractmethod
    def stop(self, config: dict[str, Any]) -> ProviderResult: ...

    @abstractmethod
    def destroy(self, config: dict[str, Any]) -> ProviderResult: ...

    @abstractmethod
    def status(self, config: dict[str, Any]) -> ProviderResult: ...

    @abstractmethod
    def execute(self, config: dict[str, Any], command: str) -> ProviderResult: ...

    @abstractmethod
    def snapshot(self, config: dict[str, Any], name: str) -> ProviderResult: ...

    @abstractmethod
    def restore(self, config: dict[str, Any], snapshot_id: str) -> ProviderResult: ...
