import pytest

from kernellab.runtime.exceptions import UnsafePathError
from kernellab.runtime.paths import RuntimePaths


@pytest.mark.unit
class TestRuntimePaths:
    def test_lab_dir(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        lab_dir = paths.lab_dir("my-lab")
        assert lab_dir == tmp_dir / "base" / "labs" / "my-lab"

    def test_serial_log(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        log = paths.serial_log("my-lab")
        assert log == tmp_dir / "base" / "labs" / "my-lab" / "serial.log"

    def test_runtime_json(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        rj = paths.runtime_json("my-lab")
        assert rj == tmp_dir / "base" / "labs" / "my-lab" / "runtime.json"

    def test_vm_dir(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        assert paths.vm_dir("my-lab") == tmp_dir / "base" / "labs" / "my-lab" / "vm"

    def test_artifacts_dir(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        assert paths.artifacts_dir("my-lab") == tmp_dir / "base" / "labs" / "my-lab" / "artifacts"

    def test_images_dir(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        assert paths.images_dir() == tmp_dir / "base" / "images"

    def test_locks_dir(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        assert paths.locks_dir() == tmp_dir / "base" / "runtime" / "locks"

    def test_ensure_lab_dirs(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        paths.ensure_lab_dirs("my-lab")
        assert paths.lab_dir("my-lab").is_dir()
        assert paths.vm_dir("my-lab").is_dir()
        assert paths.artifacts_dir("my-lab").is_dir()

    def test_safe_lab_id_valid(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        for lab_id in ["my-lab", "lab_01", "TestLab123"]:
            d = paths.lab_dir(lab_id)
            assert d.name == lab_id

    def test_unsafe_lab_id_path_traversal(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        with pytest.raises(UnsafePathError):
            paths.lab_dir("../etc/passwd")

    def test_unsafe_lab_id_special_chars(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        with pytest.raises(UnsafePathError):
            paths.lab_dir("lab;rm -rf /")

    def test_unsafe_lab_id_empty(self, tmp_dir):
        paths = RuntimePaths(base_path=tmp_dir / "base")
        with pytest.raises(UnsafePathError):
            paths.lab_dir("")
