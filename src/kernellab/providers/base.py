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
