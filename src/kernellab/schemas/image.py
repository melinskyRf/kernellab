"""Image schemas."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic needs this at runtime

from pydantic import BaseModel


class ImageCreate(BaseModel):
    name: str
    path: str
    provider: str = "virtualbox"
    format: str | None = None
    architecture: str = "x86_64"


class ImageResponse(BaseModel):
    id: str
    name: str
    provider: str
    format: str
    path: str
    architecture: str
    created_at: datetime | str | None
    metadata: dict[str, str] | None = None

    model_config = {"from_attributes": True}


class ImageListResponse(BaseModel):
    items: list[ImageResponse]
    total: int
