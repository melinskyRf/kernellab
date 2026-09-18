import pytest
from typer.testing import CliRunner

from kernellab.cli.app import app

runner = CliRunner()


@pytest.mark.cli
class TestProviderCommands:
    def test_provider_list(self, monkeypatch):
        from kernellab.providers.fake import FakeProvider
        from kernellab.providers.registry import ProviderRegistry

        registry = ProviderRegistry()
        registry.register("fake", FakeProvider)

        monkeypatch.setattr(
            "kernellab.cli.provider._get_registry", lambda: registry
        )
        result = runner.invoke(app, ["provider", "list"])
        assert result.exit_code == 0
        assert "Providers" in result.output
        assert "fake" in result.output

    def test_provider_show(self, monkeypatch):
        from kernellab.providers.fake import FakeProvider
        from kernellab.providers.registry import ProviderRegistry

        registry = ProviderRegistry()
        registry.register("fake", FakeProvider)

        monkeypatch.setattr(
            "kernellab.cli.provider._get_registry", lambda: registry
        )
        result = runner.invoke(app, ["provider", "show", "fake"])
        assert result.exit_code == 0
        assert "fake" in result.output
