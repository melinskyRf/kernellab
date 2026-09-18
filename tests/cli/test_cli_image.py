import pytest
from typer.testing import CliRunner

from kernellab.cli.app import app

runner = CliRunner()


@pytest.mark.cli
class TestImageCommands:
    def test_image_list_empty(self, monkeypatch, tmp_dir):
        db_path = tmp_dir / "test.db"

        from kernellab.images.repository import ImageRepository
        from kernellab.images.service import ImageService
        from kernellab.persistence.database import DatabaseManager

        db = DatabaseManager(database_url=f"sqlite:///{db_path}")
        db.create_tables()
        repo = ImageRepository(db)
        svc = ImageService(repo)

        monkeypatch.setattr("kernellab.cli.image._get_service", lambda: svc)
        result = runner.invoke(app, ["image", "list"])
        assert result.exit_code == 1
        assert "No images" in result.output

    def test_image_list_with_images(self, monkeypatch, tmp_dir):
        db_path = tmp_dir / "test.db"
        img_file = tmp_dir / "test.qcow2"
        img_file.touch()

        from kernellab.images.repository import ImageRepository
        from kernellab.images.service import ImageService
        from kernellab.persistence.database import DatabaseManager

        db = DatabaseManager(database_url=f"sqlite:///{db_path}")
        db.create_tables()
        repo = ImageRepository(db)
        svc = ImageService(repo)
        svc.add_image(name="test-img", path=str(img_file), provider="qemu")

        monkeypatch.setattr("kernellab.cli.image._get_service", lambda: svc)
        result = runner.invoke(app, ["image", "list"])
        assert result.exit_code == 0
        assert "test-img" in result.output
