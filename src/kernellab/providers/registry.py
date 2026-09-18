from __future__ import annotations

from kernellab.providers.base import Provider  # noqa: TC001


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, type[Provider]] = {}

    def register(self, name: str, provider_class: type[Provider]) -> None:
        self._providers[name] = provider_class

    def get(self, name: str) -> Provider:
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not registered")
        return self._providers[name]()

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())


_registry: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        from kernellab.providers.fake import FakeProvider

        _registry = ProviderRegistry()
        _registry.register("fake", FakeProvider)
    return _registry
