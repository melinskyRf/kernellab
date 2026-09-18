from __future__ import annotations

from kernellab.providers.base import Provider, ProviderInfo  # noqa: TC001


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

    def list_available_providers(self) -> list[str]:
        available: list[str] = []
        for name, cls in self._providers.items():
            try:
                provider = cls()
                info = provider.info()
                if info.available:
                    available.append(name)
            except Exception:
                continue
        return available

    def get_provider_info(self, name: str) -> ProviderInfo:
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not registered")
        provider = self._providers[name]()
        return provider.info()


_registry: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        from kernellab.providers.fake import FakeProvider
        from kernellab.providers.qemu import QEMUProvider
        from kernellab.providers.virtualbox import VirtualBoxProvider

        _registry = ProviderRegistry()
        _registry.register("fake", FakeProvider)
        _registry.register("virtualbox", VirtualBoxProvider)
        _registry.register("qemu", QEMUProvider)
    return _registry
