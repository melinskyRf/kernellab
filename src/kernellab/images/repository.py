"""Repository for Image persistence."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from kernellab.images.models import Image
from kernellab.persistence.database import DatabaseManager  # noqa: TC001
from kernellab.persistence.models import ImageModel


def _image_model_to_dict(model: ImageModel) -> dict[str, Any]:
    """Convert an ImageModel ORM instance to a domain-compatible dictionary."""
    metadata = None
    if model.metadata_json:
        try:
            metadata = json.loads(model.metadata_json)
        except (json.JSONDecodeError, TypeError):
            metadata = {}
    return {
        "id": model.id,
        "name": model.name,
        "provider": model.provider,
        "format": model.format,
        "path": model.path,
        "architecture": model.architecture,
        "created_at": model.created_at.isoformat(),
        "metadata": metadata,
    }


def _dict_to_image(data: dict[str, Any]) -> Image:
    """Convert a dictionary to an Image domain object."""
    return Image(
        id=data["id"],
        name=data["name"],
        provider=data["provider"],
        format=data["format"],
        path=data["path"],
        architecture=data["architecture"],
        created_at=datetime.fromisoformat(data["created_at"]),
        metadata=data.get("metadata") or {},
    )


class ImageRepository:
    """Repository for managing Image persistence."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def create(self, image_dict: dict[str, Any]) -> Image:
        """Create a new Image from a dictionary and persist it."""
        image = Image(
            id=image_dict["id"],
            name=image_dict["name"],
            provider=image_dict["provider"],
            format=image_dict["format"],
            path=image_dict["path"],
            architecture=image_dict.get("architecture", "x86_64"),
            created_at=datetime.fromisoformat(image_dict["created_at"]),
            metadata=image_dict.get("metadata"),
        )
        with self._db.get_session() as session:
            model = ImageModel(
                id=image.id,
                name=image.name,
                provider=image.provider,
                format=image.format,
                path=image.path,
                architecture=image.architecture,
                created_at=image.created_at,
                metadata_json=json.dumps(image.metadata) if image.metadata else None,
            )
            session.add(model)
        return image

    def get_by_id(self, image_id: str) -> Image | None:
        """Retrieve an Image by its ID."""
        with self._db.get_session() as session:
            model = session.get(ImageModel, image_id)
            if model is None:
                return None
            return _dict_to_image(_image_model_to_dict(model))

    def get_by_name(self, name: str) -> Image | None:
        """Retrieve an Image by its unique name."""
        with self._db.get_session() as session:
            model = session.query(ImageModel).filter(ImageModel.name == name).first()
            if model is None:
                return None
            return _dict_to_image(_image_model_to_dict(model))

    def get_all(self) -> list[Image]:
        """Retrieve all Images."""
        with self._db.get_session() as session:
            models = session.query(ImageModel).all()
            return [_dict_to_image(_image_model_to_dict(m)) for m in models]

    def delete(self, image_id: str) -> bool:
        """Delete an Image by its ID. Returns True if deleted, False if not found."""
        with self._db.get_session() as session:
            model = session.get(ImageModel, image_id)
            if model is None:
                return False
            session.delete(model)
            return True

    def update(self, image_id: str, data: dict[str, Any]) -> Image | None:
        """Update an Image with the given data. Returns the updated Image or None."""
        with self._db.get_session() as session:
            model = session.get(ImageModel, image_id)
            if model is None:
                return None
            if "name" in data:
                model.name = data["name"]
            if "provider" in data:
                model.provider = data["provider"]
            if "format" in data:
                model.format = data["format"]
            if "path" in data:
                model.path = data["path"]
            if "architecture" in data:
                model.architecture = data["architecture"]
            if "metadata" in data:
                metadata = data["metadata"]
                model.metadata_json = json.dumps(metadata) if metadata else None
            session.flush()
            return _dict_to_image(_image_model_to_dict(model))
