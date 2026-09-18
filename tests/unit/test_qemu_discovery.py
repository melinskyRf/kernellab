from unittest.mock import patch

import pytest

from kernellab.providers.qemu.discovery import detect
from kernellab.providers.qemu.parser import parse_qemu_version


@pytest.mark.unit
class TestQemuDiscovery:
    @patch("kernellab.providers.qemu.discovery.shutil.which", return_value=None)
    def test_discover_not_found(self, mock_which):
        result = detect()
        assert result.available is False
        assert result.system_executable == ""
        assert result.version == ""

    @patch("kernellab.providers.qemu.discovery._detect_acceleration", return_value="kvm")
    @patch("kernellab.providers.qemu.discovery._get_version", return_value="8.2.2")
    @patch(
        "kernellab.providers.qemu.discovery.shutil.which",
        side_effect=lambda exe: "/usr/bin/" + exe if exe == "qemu-system-x86_64" else None,
    )
    def test_discover_found(self, mock_which, mock_version, mock_accel):
        result = detect()
        assert result.available is True
        assert "qemu-system-x86_64" in result.system_executable
        assert result.version == "8.2.2"
        assert result.acceleration == "kvm"


@pytest.mark.unit
class TestParseQemuVersion:
    def test_parse_version_full(self):
        raw = "QEMU emulator version 8.2.2\nCopyright (c) 2003-2023 Fabrice Bellard"
        assert parse_qemu_version(raw) == "8.2.2"

    def test_parse_version_short(self):
        raw = "QEMU emulator version 7.1.0"
        assert parse_qemu_version(raw) == "7.1.0"

    def test_parse_version_no_match(self):
        raw = "some random output"
        assert parse_qemu_version(raw) == "some random output"

    def test_parse_version_empty(self):
        assert parse_qemu_version("") == ""
