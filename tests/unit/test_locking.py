import pytest

from kernellab.runtime.locking import RuntimeLock


@pytest.mark.unit
class TestRuntimeLock:
    def test_acquire_release(self, tmp_dir):
        lock = RuntimeLock(tmp_dir)
        assert lock.acquire("test-lab", timeout=5) is True
        assert lock.is_locked("test-lab") is True
        lock.release("test-lab")
        assert lock.is_locked("test-lab") is False

    def test_is_locked_false(self, tmp_dir):
        lock = RuntimeLock(tmp_dir)
        assert lock.is_locked("test-lab") is False

    def test_release_not_held(self, tmp_dir):
        lock = RuntimeLock(tmp_dir)
        lock.release("test-lab")

    def test_stale_lock(self, tmp_dir):
        lock = RuntimeLock(tmp_dir)
        lock_path = tmp_dir / "runtime" / "locks" / "test-lab.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("99999999")
        assert lock.is_locked("test-lab") is False
        assert not lock_path.exists()

    def test_acquire_timeout(self, tmp_dir):
        import os
        lock_path = tmp_dir / "runtime" / "locks" / "test-lab.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("99999999")
        lock = RuntimeLock(tmp_dir)
        acquired = lock.acquire("test-lab", timeout=0)
        assert acquired is True
        assert lock_path.read_text().strip() == str(os.getpid())
        lock.release("test-lab")
