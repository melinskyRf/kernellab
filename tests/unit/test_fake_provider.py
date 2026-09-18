import pytest

from kernellab.providers.fake import FakeProvider


@pytest.mark.unit
class TestFakeProvider:
    def test_create(self, fake_provider: FakeProvider):
        result = fake_provider.create({"name": "test"})
        assert result.success is True
        assert result.message == "created"
        assert result.data["environment_id"] == "fake-env-001"

    def test_start(self, fake_provider: FakeProvider):
        result = fake_provider.start({"name": "test"})
        assert result.success is True
        assert result.message == "started"
        assert result.data["machine_id"] == "fake-machine-001"

    def test_stop(self, fake_provider: FakeProvider):
        result = fake_provider.stop({"name": "test"})
        assert result.success is True
        assert result.message == "stopped"

    def test_destroy(self, fake_provider: FakeProvider):
        result = fake_provider.destroy({"name": "test"})
        assert result.success is True
        assert result.message == "destroyed"

    def test_status(self, fake_provider: FakeProvider):
        result = fake_provider.status({"name": "test"})
        assert result.success is True
        assert result.message == "running"

    def test_execute(self, fake_provider: FakeProvider):
        result = fake_provider.execute({"name": "test"}, "echo hello")
        assert result.success is True
        assert result.message == "completed"
        assert result.data["command"] == "echo hello"
        assert result.data["exit_code"] == 0
        assert "test completed" in result.logs

    def test_execute_failure(self, fake_provider: FakeProvider):
        config = {"provider_options": {"fail_on_run": True}}
        result = fake_provider.execute(config, "echo hello")
        assert result.success is False
        assert result.message == "Simulated failure"

    def test_snapshot(self, fake_provider: FakeProvider):
        result = fake_provider.snapshot({"name": "test"}, "snap-1")
        assert result.success is True
        assert result.data["snapshot_id"] == "fake-snap-snap-1"

    def test_restore(self, fake_provider: FakeProvider):
        result = fake_provider.restore({"name": "test"}, "fake-snap-1")
        assert result.success is True
        assert result.data["snapshot_id"] == "fake-snap-1"
