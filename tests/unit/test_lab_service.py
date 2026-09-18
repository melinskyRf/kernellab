import pytest

from kernellab.application.lab_service import LabService
from kernellab.domain.enums import LabStatus, ProviderType
from kernellab.exceptions import LabAlreadyExistsError, LabNotFoundError


@pytest.mark.unit
class TestCreateLab:
    def test_create_lab(self, lab_service: LabService):
        lab = lab_service.create_lab(name="my-test-lab")
        assert lab.name == "my-test-lab"
        assert lab.provider == ProviderType.FAKE
        assert lab.status == LabStatus.CREATED

    @pytest.mark.parametrize(
        "bad_name",
        ["ab", "a", "", "lab name!", "lab@name", "valid-lab"],
        ids=["too-short-2", "too-short-1", "empty", "space", "at-sign", "valid-but-separate-test"],
    )
    def test_create_lab_invalid_name(self, lab_service: LabService, bad_name: str):
        if bad_name == "valid-lab":
            # valid name, just ensures it does NOT raise
            lab = lab_service.create_lab(name=bad_name)
            assert lab.name == bad_name
        else:
            with pytest.raises(ValueError, match="Invalid lab name"):
                lab_service.create_lab(name=bad_name)

    def test_create_lab_duplicate(self, lab_service: LabService):
        lab_service.create_lab(name="dup-lab")
        with pytest.raises(LabAlreadyExistsError):
            lab_service.create_lab(name="dup-lab")


@pytest.mark.unit
class TestGetLab:
    def test_get_lab(self, lab_service: LabService):
        created = lab_service.create_lab(name="get-me")
        fetched = lab_service.get_lab(lab_id=created.id)
        assert fetched.id == created.id
        assert fetched.name == "get-me"

    def test_get_lab_by_name(self, lab_service: LabService):
        created = lab_service.create_lab(name="by-name")
        fetched = lab_service.get_lab(name="by-name")
        assert fetched.id == created.id

    def test_get_lab_not_found(self, lab_service: LabService):
        with pytest.raises(LabNotFoundError):
            lab_service.get_lab(lab_id="nonexistent-id")


@pytest.mark.unit
class TestListLabs:
    def test_list_labs(self, lab_service: LabService):
        lab_service.create_lab(name="lab-one")
        lab_service.create_lab(name="lab-two")
        labs = lab_service.list_labs()
        assert len(labs) == 2
        names = {lab.name for lab in labs}
        assert names == {"lab-one", "lab-two"}


@pytest.mark.unit
class TestDeleteLab:
    def test_delete_lab(self, lab_service: LabService):
        lab = lab_service.create_lab(name="delete-me")
        result = lab_service.delete_lab(lab.id)
        assert result is True
        with pytest.raises(LabNotFoundError):
            lab_service.get_lab(lab_id=lab.id)

    def test_delete_lab_not_found(self, lab_service: LabService):
        with pytest.raises(LabNotFoundError):
            lab_service.delete_lab("nonexistent-id")
