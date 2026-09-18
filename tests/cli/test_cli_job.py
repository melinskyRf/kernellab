
import pytest
from typer.testing import CliRunner

from kernellab.cli.app import app

runner = CliRunner()


@pytest.mark.cli
class TestJobCommands:
    def test_job_list(self, tmp_dir, monkeypatch):
        dot_dir = tmp_dir / ".kernellab"
        dot_dir.mkdir()
        (dot_dir / "logs").mkdir()
        (dot_dir / "artifacts").mkdir()
        (dot_dir / "runtime").mkdir()
        db_path = dot_dir / "kernellab.db"

        monkeypatch.setenv("KERNELLAB_DB_URL", f"sqlite:///{db_path}")
        monkeypatch.chdir(tmp_dir)
        result = runner.invoke(app, ["job", "list"])
        assert result.exit_code == 1
        assert "No jobs found" in result.output
