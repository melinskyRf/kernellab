import httpx
import pytest

from kernellab.persistence.database import DatabaseManager
from kernellab.providers.base import ProviderCapabilities, ProviderInfo


@pytest.fixture
def fake_registry():
    from kernellab.providers.fake import FakeProvider
    from kernellab.providers.registry import ProviderRegistry

    registry = ProviderRegistry()
    registry.register("fake", FakeProvider)

    original_info = registry.get_provider_info

    def patched_get_provider_info(name):
        if name == "fake":
            return ProviderInfo(
                available=True,
                version="0.1.0-test",
                executable="/usr/bin/fake",
                host_info="test-host",
            )
        return original_info(name)

    registry.get_provider_info = patched_get_provider_info

    original_get = registry.get

    def patched_get(name):
        provider = original_get(name)
        if name == "fake":
            provider.info = lambda: patched_get_provider_info(name)
            provider.capabilities = lambda: ProviderCapabilities(
                create=False, start=False, stop=False, destroy=False,
                serial=False, snapshots=False, guest_exec=False,
            )
        return provider

    registry.get = patched_get
    return registry


@pytest.fixture
def test_app(db_url, fake_registry):
    from kernellab.api import dependencies
    from kernellab.api.app import create_app
    from kernellab.api.routes import providers as providers_module

    db = DatabaseManager(database_url=db_url)
    db.create_tables()

    app = create_app()

    def override_get_database_manager():
        yield db

    app.dependency_overrides[dependencies.get_database_manager] = override_get_database_manager

    original = providers_module.get_provider_registry
    providers_module.get_provider_registry = lambda: fake_registry

    yield app

    providers_module.get_provider_registry = original
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    transport = httpx.ASGITransport(app=test_app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_providers(client):
    response = await client.get("/api/v1/providers")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    names = [p["name"] for p in data["items"]]
    assert "fake" in names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_provider(client):
    response = await client.get("/api/v1/providers/fake")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "fake"
    assert data["available"] is True
    assert data["version"] == "0.1.0-test"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_provider_not_found(client):
    response = await client.get("/api/v1/providers/nonexistent")
    assert response.status_code == 404
