"""Repository classes for Kernel Lab persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from kernellab.domain.enums import JobStatus, JobType, LabStatus, ProviderType
from kernellab.domain.job import Job
from kernellab.domain.lab import Lab
from kernellab.persistence.database import DatabaseManager  # noqa: TC001
from kernellab.persistence.models import JobModel, LabModel


def _lab_model_to_dict(model: LabModel) -> dict[str, Any]:
    """Convert a LabModel ORM instance to a domain-compatible dictionary."""
    config = None
    if model.configuration:
        try:
            config = json.loads(model.configuration)
        except (json.JSONDecodeError, TypeError):
            config = {}
    return {
        "id": model.id,
        "name": model.name,
        "description": model.description,
        "provider": model.provider,
        "status": model.status,
        "configuration": config,
        "created_at": model.created_at.isoformat(),
        "updated_at": model.updated_at.isoformat(),
    }


def _job_model_to_dict(model: JobModel) -> dict[str, Any]:
    """Convert a JobModel ORM instance to a domain-compatible dictionary."""
    return {
        "id": model.id,
        "lab_id": model.lab_id,
        "type": model.type,
        "status": model.status,
        "created_at": model.created_at.isoformat(),
        "started_at": model.started_at.isoformat() if model.started_at else None,
        "finished_at": model.finished_at.isoformat() if model.finished_at else None,
        "exit_code": model.exit_code,
        "error": model.error,
        "logs": model.logs or "",
    }


def _dict_to_lab(data: dict[str, Any]) -> Lab:
    """Convert a dictionary to a Lab domain object."""
    return Lab(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        provider=ProviderType(data["provider"]),
        status=LabStatus(data["status"]),
        configuration=data.get("configuration") or {},
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


def _dict_to_job(data: dict[str, Any]) -> Job:
    """Convert a dictionary to a Job domain object."""
    return Job(
        id=data["id"],
        lab_id=data["lab_id"],
        type=JobType(data["type"]),
        status=JobStatus(data["status"]),
        created_at=datetime.fromisoformat(data["created_at"]),
        started_at=(
            datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        ),
        finished_at=(
            datetime.fromisoformat(data["finished_at"]) if data.get("finished_at") else None
        ),
        exit_code=data.get("exit_code"),
        error=data.get("error"),
        logs=data.get("logs", ""),
    )


class LabRepository:
    """Repository for managing Lab persistence."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def create(self, lab_dict: dict[str, Any]) -> Lab:
        """Create a new Lab from a dictionary and persist it."""
        lab = Lab(
            id=lab_dict["id"],
            name=lab_dict["name"],
            description=lab_dict.get("description"),
            provider=ProviderType(lab_dict["provider"]),
            status=LabStatus(lab_dict["status"]),
            configuration=lab_dict.get("configuration") or {},
            created_at=datetime.fromisoformat(lab_dict["created_at"]),
            updated_at=datetime.fromisoformat(lab_dict["updated_at"]),
        )
        with self._db.get_session() as session:
            model = LabModel(
                id=lab.id,
                name=lab.name,
                description=lab.description,
                provider=lab.provider.value,
                status=lab.status.value,
                configuration=json.dumps(lab.configuration) if lab.configuration else None,
                created_at=lab.created_at,
                updated_at=lab.updated_at,
            )
            session.add(model)
        return lab

    def get_by_id(self, lab_id: str) -> Lab | None:
        """Retrieve a Lab by its ID."""
        with self._db.get_session() as session:
            model = session.get(LabModel, lab_id)
            if model is None:
                return None
            return _dict_to_lab(_lab_model_to_dict(model))

    def get_by_name(self, name: str) -> Lab | None:
        """Retrieve a Lab by its unique name."""
        with self._db.get_session() as session:
            model = session.query(LabModel).filter(LabModel.name == name).first()
            if model is None:
                return None
            return _dict_to_lab(_lab_model_to_dict(model))

    def get_all(self) -> list[Lab]:
        """Retrieve all Labs."""
        with self._db.get_session() as session:
            models = session.query(LabModel).all()
            return [_dict_to_lab(_lab_model_to_dict(m)) for m in models]

    def delete(self, lab_id: str) -> bool:
        """Delete a Lab by its ID. Returns True if deleted, False if not found."""
        with self._db.get_session() as session:
            model = session.get(LabModel, lab_id)
            if model is None:
                return False
            session.delete(model)
            return True

    def update(self, lab_id: str, data: dict[str, Any]) -> Lab | None:
        """Update a Lab with the given data. Returns the updated Lab or None."""
        with self._db.get_session() as session:
            model = session.get(LabModel, lab_id)
            if model is None:
                return None
            if "name" in data:
                model.name = data["name"]
            if "description" in data:
                model.description = data["description"]
            if "provider" in data:
                model.provider = data["provider"]
            if "status" in data:
                model.status = data["status"]
            if "configuration" in data:
                config = data["configuration"]
                model.configuration = json.dumps(config) if config else None
            model.updated_at = datetime.now(UTC)
            session.flush()
            return _dict_to_lab(_lab_model_to_dict(model))


class JobRepository:
    """Repository for managing Job persistence."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def create(self, job_dict: dict[str, Any]) -> Job:
        """Create a new Job from a dictionary and persist it."""
        job = Job(
            id=job_dict["id"],
            lab_id=job_dict["lab_id"],
            type=JobType(job_dict["type"]),
            status=JobStatus(job_dict["status"]),
            created_at=datetime.fromisoformat(job_dict["created_at"]),
            started_at=(
                datetime.fromisoformat(job_dict["started_at"])
                if job_dict.get("started_at")
                else None
            ),
            finished_at=(
                datetime.fromisoformat(job_dict["finished_at"])
                if job_dict.get("finished_at")
                else None
            ),
            exit_code=job_dict.get("exit_code"),
            error=job_dict.get("error"),
            logs=job_dict.get("logs", ""),
        )
        with self._db.get_session() as session:
            model = JobModel(
                id=job.id,
                lab_id=job.lab_id,
                type=job.type.value,
                status=job.status.value,
                created_at=job.created_at,
                started_at=job.started_at,
                finished_at=job.finished_at,
                exit_code=job.exit_code,
                error=job.error,
                logs=job.logs,
            )
            session.add(model)
        return job

    def get_by_id(self, job_id: str) -> Job | None:
        """Retrieve a Job by its ID."""
        with self._db.get_session() as session:
            model = session.get(JobModel, job_id)
            if model is None:
                return None
            return _dict_to_job(_job_model_to_dict(model))

    def get_by_lab_id(self, lab_id: str) -> list[Job]:
        """Retrieve all Jobs associated with a specific Lab."""
        with self._db.get_session() as session:
            models = session.query(JobModel).filter(JobModel.lab_id == lab_id).all()
            return [_dict_to_job(_job_model_to_dict(m)) for m in models]

    def get_all(self) -> list[Job]:
        """Retrieve all Jobs."""
        with self._db.get_session() as session:
            models = session.query(JobModel).all()
            return [_dict_to_job(_job_model_to_dict(m)) for m in models]

    def update(self, job_id: str, data: dict[str, Any]) -> Job | None:
        """Update a Job with the given data. Returns the updated Job or None."""
        with self._db.get_session() as session:
            model = session.get(JobModel, job_id)
            if model is None:
                return None
            if "lab_id" in data:
                model.lab_id = data["lab_id"]
            if "type" in data:
                model.type = data["type"]
            if "status" in data:
                model.status = data["status"]
            if "started_at" in data:
                model.started_at = data["started_at"]
            if "finished_at" in data:
                model.finished_at = data["finished_at"]
            if "exit_code" in data:
                model.exit_code = data["exit_code"]
            if "error" in data:
                model.error = data["error"]
            if "logs" in data:
                model.logs = data["logs"]
            session.flush()
            return _dict_to_job(_job_model_to_dict(model))
