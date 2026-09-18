from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic needs this at runtime

from pydantic import BaseModel


class LabCreate(BaseModel):
    name: str
    description: str | None = None
    provider: str = "fake"
    configuration: dict[str, str] = {}


class LabResponse(BaseModel):
    id: str
    name: str
    description: str | None
    provider: str
    status: str
    configuration: dict[str, str]
    created_at: datetime | str | None
    updated_at: datetime | str | None

    model_config = {"from_attributes": True}


class LabListResponse(BaseModel):
    items: list[LabResponse]
    total: int


class LabRunResponse(BaseModel):
    job_id: str
    status: str
    message: str


class LabUpResponse(BaseModel):
    lab_id: str
    status: str
    message: str


class LabStatusResponse(BaseModel):
    lab_id: str
    status: str
    running: bool
    details: dict[str, str] = {}


class LabConsoleResponse(BaseModel):
    lab_id: str
    logs: str
    message: str
