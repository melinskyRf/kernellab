import pytest

from kernellab.exceptions import ImageAlreadyExistsError, ImageNotFoundError
from kernellab.images.repository import ImageRepository
from kernellab.images.service import ImageService
from kernellab.persistence.database import DatabaseManager


@pytest.fixture
def image_service(tmp_dir):
    db_path = tmp_dir / "test.db"
    db = DatabaseManager(database_url=f"sqlite:///{db_path}")
    db.create_tables()
    repo = ImageRepository(db)
    return ImageService(repo)


@pytest.mark.unit
class TestImageService:
    def test_add_image(self, tmp_dir, image_service):
        img_file = tmp_dir / "test.qcow2"
        img_file.touch()
        image = image_service.add_image(
            name="test-img",
            path=str(img_file),
            provider="qemu",
            format="qcow2",
        )
        assert image.name == "test-img"
        assert image.format == "qcow2"
        assert image.provider == "qemu"

    def test_add_image_invalid_path(self, tmp_dir, image_service):
        with pytest.raises(FileNotFoundError):
            image_service.add_image(
                name="test-img",
                path="/nonexistent/path/test.qcow2",
                provider="qemu",
            )

    def test_add_image_duplicate(self, tmp_dir, image_service):
        img_file = tmp_dir / "test.qcow2"
        img_file.touch()
        image_service.add_image(name="test-img", path=str(img_file), provider="qemu")
        with pytest.raises(ImageAlreadyExistsError):
            image_service.add_image(name="test-img", path=str(img_file), provider="qemu")

    def test_list_images(self, tmp_dir, image_service):
        assert image_service.list_images() == []
        img_file = tmp_dir / "test.qcow2"
        img_file.touch()
        image_service.add_image(name="test-img", path=str(img_file), provider="qemu")
        images = image_service.list_images()
        assert len(images) == 1
        assert images[0].name == "test-img"

    def test_get_image(self, tmp_dir, image_service):
        img_file = tmp_dir / "test.qcow2"
        img_file.touch()
        created = image_service.add_image(name="test-img", path=str(img_file), provider="qemu")
        found = image_service.get_image("test-img")
        assert found.id == created.id

    def test_get_image_not_found(self, tmp_dir, image_service):
        with pytest.raises(ImageNotFoundError):
            image_service.get_image("nonexistent")

    def test_remove_image(self, tmp_dir, image_service):
        img_file = tmp_dir / "test.qcow2"
        img_file.touch()
        image_service.add_image(name="test-img", path=str(img_file), provider="qemu")
        assert image_service.remove_image("test-img") is True
        assert image_service.list_images() == []

    def test_remove_image_not_found(self, tmp_dir, image_service):
        with pytest.raises(ImageNotFoundError):
            image_service.remove_image("nonexistent")
