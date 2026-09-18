"""Lab endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from kernellab.api.dependencies import get_lab_service, get_runtime_service
from kernellab.application.lab_service import LabService  # noqa: TC001
from kernellab.application.runtime_service import RuntimeService  # noqa: TC001
from kernellab.exceptions import (
    KernelLabError,
    LabAlreadyExistsError,
    LabNotFoundError,
)
from kernellab.schemas.lab import LabCreate, LabListResponse, LabResponse, LabRunResponse

router = APIRouter(prefix="/labs", tags=["labs"])


@router.post("", response_model=LabResponse, status_code=201)
async def create_lab(
    lab_data: LabCreate,
    lab_service: Annotated[LabService, Depends(get_lab_service)],
) -> LabResponse:
    """Create a new lab."""
    try:
        lab = lab_service.create_lab(
            name=lab_data.name,
            description=lab_data.description,
            provider=lab_data.provider,
            configuration=lab_data.configuration,
        )
        return LabResponse.model_validate(lab)
    except LabAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e.message)) from None
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.get("", response_model=LabListResponse)
async def list_labs(
    lab_service: Annotated[LabService, Depends(get_lab_service)],
) -> LabListResponse:
    """List all labs."""
    try:
        labs = lab_service.list_labs()
        items = [LabResponse.model_validate(lab) for lab in labs]
        return LabListResponse(items=items, total=len(items))
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.get("/{lab_id}", response_model=LabResponse)
async def get_lab(
    lab_id: str,
    lab_service: Annotated[LabService, Depends(get_lab_service)],
) -> LabResponse:
    """Get a lab by ID."""
    try:
        lab = lab_service.get_lab(lab_id=lab_id)
        return LabResponse.model_validate(lab)
    except LabNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.delete("/{lab_id}")
async def delete_lab(
    lab_id: str,
    lab_service: Annotated[LabService, Depends(get_lab_service)],
) -> dict[str, str]:
    """Delete a lab."""
    try:
        lab_service.delete_lab(lab_id)
        return {"message": "Lab deleted"}
    except LabNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.post("/{lab_id}/run", response_model=LabRunResponse)
async def run_lab(
    lab_id: str,
    lab_service: Annotated[LabService, Depends(get_lab_service)],
    runtime_service: Annotated[RuntimeService, Depends(get_runtime_service)],
) -> LabRunResponse:
    """Run a lab."""
    try:
        lab = lab_service.get_lab(lab_id=lab_id)
        from kernellab.config.loader import KernellabConfig

        config = KernellabConfig(
            name=lab.name,
            description=lab.description,
            provider=lab.provider.value,
            **lab.configuration,
        )
        job, logs = runtime_service.run_lab(config, lab_id)
        return LabRunResponse(
            job_id=job.id,
            status=job.status.value,
            message="Lab execution started",
        )
    except LabNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None
