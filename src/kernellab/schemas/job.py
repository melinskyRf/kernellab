
from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: str
    lab_id: str
    type: str
    status: str
    created_at: datetime | str | None
    started_at: datetime | str | None
    finished_at: datetime | str | None
    exit_code: int | None
    error: str | None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int


class JobLogsResponse(BaseModel):
    job_id: str
    logs: str | None
