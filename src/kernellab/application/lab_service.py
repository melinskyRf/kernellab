from __future__ import annotations

import re

from kernellab.domain.enums import ProviderType
from kernellab.domain.lab import Lab
from kernellab.exceptions import LabAlreadyExistsError, LabNotFoundError
from kernellab.logging import get_logger
from kernellab.persistence.repositories import LabRepository  # noqa: TC001

logger = get_logger(__name__)

_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")


class LabService:
    def __init__(self, repo: LabRepository) -> None:
        self._repo = repo

    def create_lab(
        self,
        name: str,
        description: str | None = None,
        provider: str = "fake",
        configuration: dict | None = None,
    ) -> Lab:
        if not self.validate_lab_name(name):
            raise ValueError(f"Invalid lab name: {name!r}")
        existing = self._repo.get_by_name(name)
        if existing is not None:
            raise LabAlreadyExistsError(name)
        lab = Lab(
            name=name,
            description=description,
            provider=ProviderType(provider),
            configuration=configuration,
        )
        created = self._repo.create(lab.to_dict())
        logger.info("Created lab %r (id=%s)", name, created.id)
        return created

    def get_lab(self, lab_id: str | None = None, name: str | None = None) -> Lab:
        if lab_id is not None:
            lab = self._repo.get_by_id(lab_id)
        elif name is not None:
            lab = self._repo.get_by_name(name)
        else:
            raise ValueError("Either lab_id or name must be provided")
        if lab is None:
            identifier = lab_id or name
            raise LabNotFoundError(str(identifier))
        return lab

    def list_labs(self) -> list[Lab]:
        return self._repo.get_all()

    def delete_lab(self, lab_id: str) -> bool:
        deleted = self._repo.delete(lab_id)
        if not deleted:
            raise LabNotFoundError(lab_id)
        logger.info("Deleted lab %s", lab_id)
        return True

    def validate_lab_name(self, name: str) -> bool:
        return _NAME_PATTERN.match(name) is not None
