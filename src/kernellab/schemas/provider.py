"""Provider schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ProviderCapabilitiesSchema(BaseModel):
    create: bool
    start: bool
    stop: bool
    destroy: bool
    serial: bool = False
    snapshots: bool = False
    guest_exec: bool = False


class ProviderResponse(BaseModel):
    name: str
    available: bool
    version: str
    executable: str
    host_info: str = ""
    capabilities: ProviderCapabilitiesSchema | None = None


class ProviderListResponse(BaseModel):
    items: list[ProviderResponse]
    total: int
