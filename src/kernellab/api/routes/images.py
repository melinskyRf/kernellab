"""Image endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from kernellab.api.dependencies import get_image_service
from kernellab.exceptions import (
    ImageAlreadyExistsError,
    ImageNotFoundError,
    KernelLabError,
)
from kernellab.images.service import ImageService  # noqa: TC001
from kernellab.schemas.image import ImageCreate, ImageListResponse, ImageResponse

router = APIRouter(prefix="/images", tags=["images"])


@router.get("", response_model=ImageListResponse)
async def list_images(
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> ImageListResponse:
    """List all registered images."""
    try:
        images = image_service.list_images()
        items = [ImageResponse.model_validate(img.to_dict()) for img in images]
        return ImageListResponse(items=items, total=len(items))
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.post("", response_model=ImageResponse, status_code=201)
async def register_image(
    image_data: ImageCreate,
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> ImageResponse:
    """Register a new image."""
    try:
        image = image_service.add_image(
            name=image_data.name,
            path=image_data.path,
            provider=image_data.provider,
            format=image_data.format,
            architecture=image_data.architecture,
        )
        return ImageResponse.model_validate(image.to_dict())
    except ImageAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e.message)) from None
    except FileNotFoundError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> ImageResponse:
    """Get image details."""
    try:
        image = image_service.get_image(image_id)
        return ImageResponse.model_validate(image.to_dict())
    except ImageNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> dict[str, str]:
    """Remove image registration."""
    try:
        image_service.remove_image(image_id)
        return {"message": "Image removed"}
    except ImageNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message)) from None
    except KernelLabError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from None
