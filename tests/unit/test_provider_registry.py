import pytest

from kernellab.providers.fake import FakeProvider
from kernellab.providers.registry import ProviderRegistry


@pytest.mark.unit
class TestProviderRegistry:
    def test_register_provider(self, provider_registry: ProviderRegistry):
        assert "fake" in provider_registry.list_providers()

    def test_get_provider(self, provider_registry: ProviderRegistry):
        provider = provider_registry.get("fake")
        assert isinstance(provider, FakeProvider)

    def test_get_provider_not_found(self, provider_registry: ProviderRegistry):
        with pytest.raises(KeyError, match="Provider 'nonexistent' not registered"):
            provider_registry.get("nonexistent")

    def test_list_providers(self, provider_registry: ProviderRegistry):
        providers = provider_registry.list_providers()
        assert isinstance(providers, list)
        assert "fake" in providers
