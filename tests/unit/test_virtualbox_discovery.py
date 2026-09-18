from unittest.mock import patch

import pytest

from kernellab.providers.virtualbox.discovery import detect
from kernellab.providers.virtualbox.parser import parse_vm_info, parse_vm_state


@pytest.mark.unit
class TestVirtualBoxDiscovery:
    @patch("kernellab.providers.virtualbox.discovery.shutil.which", return_value=None)
    def test_discover_not_found(self, mock_which):
        result = detect()
        assert result.available is False
        assert result.executable == ""
        assert result.version == ""

    @patch(
        "kernellab.providers.virtualbox.discovery._get_version",
        return_value="7.0.14",
    )
    @patch(
        "kernellab.providers.virtualbox.discovery.shutil.which",
        return_value="/usr/bin/VBoxManage",
    )
    def test_discover_found(self, mock_which, mock_version):
        result = detect()
        assert result.available is True
        assert result.executable == "/usr/bin/VBoxManage"
        assert result.version == "7.0.14"
        assert result.host_info != ""


@pytest.mark.unit
class TestParseVmInfo:
    def test_parse_vm_info(self):
        raw = (
            'VMState="running"\n'
            'VMName="test-vm"\n'
            'memorySize=2048\n'
            'cpus=2\n'
        )
        info = parse_vm_info(raw)
        assert info["VMState"] == "running"
        assert info["VMName"] == "test-vm"
        assert info["memorySize"] == "2048"
        assert info["cpus"] == "2"

    def test_parse_vm_info_empty(self):
        info = parse_vm_info("")
        assert info == {}

    def test_parse_vm_info_no_quotes(self):
        raw = "VMState=running\n"
        info = parse_vm_info(raw)
        assert info["VMState"] == "running"

    def test_parse_vm_state_running(self):
        info = {"VMState": "running"}
        assert parse_vm_state(info) == "RUNNING"

    def test_parse_vm_state_poweroff(self):
        info = {"VMState": "poweroff"}
        assert parse_vm_state(info) == "STOPPED"

    def test_parse_vm_state_saved(self):
        info = {"VMState": "saved"}
        assert parse_vm_state(info) == "STOPPED"

    def test_parse_vm_state_aborted(self):
        info = {"VMState": "aborted"}
        assert parse_vm_state(info) == "FAILED"

    def test_parse_vm_state_paused(self):
        info = {"VMState": "paused"}
        assert parse_vm_state(info) == "STOPPED"

    def test_parse_vm_state_stuck(self):
        info = {"VMState": "stuck"}
        assert parse_vm_state(info) == "FAILED"

    def test_parse_vm_state_unknown(self):
        info = {"VMState": "something_else"}
        assert parse_vm_state(info) == "UNKNOWN"

    def test_parse_vm_state_empty(self):
        assert parse_vm_state({}) == "UNKNOWN"
