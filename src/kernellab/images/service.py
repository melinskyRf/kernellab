"""Image service layer."""

from __future__ import annotations

from pathlib import Path

from kernellab.exceptions import ImageAlreadyExistsError, ImageNotFoundError
from kernellab.images.models import Image
from kernellab.images.repository import ImageRepository  # noqa: TC001
from kernellab.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_FORMATS = {"ova", "vmdk", "qcow2", "vdi", "raw"}
FORMAT_EXTENSIONS = {
    ".ova": "ova",
    ".vmdk": "vmdk",
    ".qcow2": "qcow2",
    ".vdi": "vdi",
    ".raw": "raw",
}


class ImageService:
    def __init__(self, repo: ImageRepository) -> None:
        self._repo = repo

    def add_image(
        self,
        name: str,
        path: str,
        provider: str = "virtualbox",
        format: str | None = None,
        architecture: str = "x86_64",
    ) -> Image:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")

        if format is None:
            format = FORMAT_EXTENSIONS.get(file_path.suffix.lower())
            if format is None:
                raise ValueError(
                    f"Cannot auto-detect format from extension {file_path.suffix!r}. "
                    f"Please specify format explicitly."
                )
        elif format not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {format!r}. "
                f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )

        existing = self._repo.get_by_name(name)
        if existing is not None:
            raise ImageAlreadyExistsError(name)

        image = Image(
            name=name,
            provider=provider,
            format=format,
            path=str(file_path.resolve()),
            architecture=architecture,
        )
        created = self._repo.create(image.to_dict())
        logger.info("Added image %r (id=%s, format=%s)", name, created.id, format)
        return created

    def list_images(self) -> list[Image]:
        return self._repo.get_all()

    def get_image(self, name_or_id: str) -> Image:
        image = self._repo.get_by_id(name_or_id)
        if image is not None:
            return image
        image = self._repo.get_by_name(name_or_id)
        if image is not None:
            return image
        raise ImageNotFoundError(name_or_id)

    def remove_image(self, name_or_id: str) -> bool:
        image = self.get_image(name_or_id)
        deleted = self._repo.delete(image.id)
        if not deleted:
            raise ImageNotFoundError(name_or_id)
        logger.info("Removed image record %r (id=%s)", image.name, image.id)
        return True
