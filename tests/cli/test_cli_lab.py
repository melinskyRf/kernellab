from pathlib import Path

import pytest
from typer.testing import CliRunner

from kernellab.cli.app import app

runner = CliRunner()


@pytest.mark.cli
class TestVersionHelp:
    def test_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Kernel Lab" in result.output

    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Kernel Lab" in result.output or "kernellab" in result.output


@pytest.mark.cli
class TestInit:
    def test_init(self, tmp_dir, monkeypatch):
        monkeypatch.chdir(tmp_dir)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert (tmp_dir / "kernellab.yaml").exists()
        assert (tmp_dir / ".kernellab").is_dir()
        assert (tmp_dir / ".kernellab" / "logs").is_dir()
        assert (tmp_dir / ".kernellab" / "artifacts").is_dir()


@pytest.mark.cli
class TestLabCommands:
    def test_lab_create(self, tmp_dir, monkeypatch):
        dot_dir = tmp_dir / ".kernellab"
        dot_dir.mkdir()
        (dot_dir / "logs").mkdir()
        (dot_dir / "artifacts").mkdir()
        (dot_dir / "runtime").mkdir()
        db_path = dot_dir / "kernellab.db"

        monkeypatch.setenv("KERNELLAB_DB_URL", f"sqlite:///{db_path}")
        monkeypatch.chdir(tmp_dir)
        result = runner.invoke(app, ["lab", "create", "test-lab"])
        assert result.exit_code == 0
        assert "created" in result.output.lower() or "test-lab" in result.output

    def test_lab_list(self, tmp_dir, monkeypatch):
        dot_dir = tmp_dir / ".kernellab"
        dot_dir.mkdir()
        (dot_dir / "logs").mkdir()
        (dot_dir / "artifacts").mkdir()
        (dot_dir / "runtime").mkdir()
        db_path = dot_dir / "kernellab.db"

        monkeypatch.setenv("KERNELLAB_DB_URL", f"sqlite:///{db_path}")
        monkeypatch.chdir(tmp_dir)

        result = runner.invoke(app, ["lab", "create", "list-lab-1"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["lab", "list"])
        assert result.exit_code == 0
        assert "list-lab-1" in result.output


@pytest.mark.cli
class TestConfigCommands:
    def test_config_validate(self, sample_config, tmp_dir, monkeypatch):
        config_path = Path(sample_config)
        monkeypatch.chdir(config_path.parent)
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
