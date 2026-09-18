import pytest
from typer.testing import CliRunner

from kernellab.cli.app import app

runner = CliRunner()


@pytest.mark.cli
class TestDoctorCommand:
    def test_doctor(self, monkeypatch, tmp_dir):
        monkeypatch.setattr(
            "kernellab.cli.doctor._check_database",
            lambda: ("Database", "SKIP", "test"),
        )
        monkeypatch.setattr(
            "kernellab.cli.doctor._check_virtualbox",
            lambda: ("VirtualBox", "SKIP", "test"),
        )
        monkeypatch.setattr(
            "kernellab.cli.doctor._check_qemu",
            lambda: ("QEMU", "SKIP", "test"),
        )
        monkeypatch.setattr(
            "kernellab.cli.doctor._check_kvm",
            lambda: ("KVM", "SKIP", "test"),
        )
        result = runner.invoke(app, ["doctor", "doctor"])
        assert result.exit_code == 0
        assert "System Health" in result.output
