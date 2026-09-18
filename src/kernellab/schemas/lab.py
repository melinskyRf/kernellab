
from datetime import datetime

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
