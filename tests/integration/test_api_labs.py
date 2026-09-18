import httpx
import pytest

from kernellab.persistence.database import DatabaseManager


@pytest.fixture
def test_app(db_url):
    from kernellab.api import dependencies
    from kernellab.api.app import create_app
    from kernellab.application.job_service import JobService
    from kernellab.application.lab_service import LabService
    from kernellab.application.runtime_service import RuntimeService
    from kernellab.persistence.repositories import JobRepository, LabRepository
    from kernellab.providers.fake import FakeProvider
    from kernellab.providers.registry import ProviderRegistry

    db = DatabaseManager(database_url=db_url)
    db.create_tables()

    lab_repo = LabRepository(db)
    job_repo = JobRepository(db)
    lab_service = LabService(lab_repo)
    job_service = JobService(job_repo)

    registry = ProviderRegistry()
    registry.register("fake", FakeProvider)
    runtime_service = RuntimeService(job_service, registry)

    def override_get_database_manager():
        yield db

    def override_get_lab_service():
        return lab_service

    def override_get_job_service():
        return job_service

    def override_get_runtime_service():
        return runtime_service

    app = create_app()
    app.dependency_overrides[dependencies.get_database_manager] = override_get_database_manager
    app.dependency_overrides[dependencies.get_lab_service] = override_get_lab_service
    app.dependency_overrides[dependencies.get_job_service] = override_get_job_service
    app.dependency_overrides[dependencies.get_runtime_service] = override_get_runtime_service

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    from httpx import ASGITransport
    transport = ASGITransport(app=test_app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "kernellab"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_lab(client):
    response = await client.post(
        "/api/v1/labs",
        json={"name": "api-test-lab"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "api-test-lab"
    assert data["provider"] == "fake"
    assert data["status"] == "created"
    assert "id" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_labs(client):
    await client.post("/api/v1/labs", json={"name": "list-lab-1"})
    await client.post("/api/v1/labs", json={"name": "list-lab-2"})
    response = await client.get("/api/v1/labs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_lab(client):
    create_resp = await client.post("/api/v1/labs", json={"name": "get-lab"})
    lab_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/labs/{lab_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "get-lab"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_lab(client):
    create_resp = await client.post("/api/v1/labs", json={"name": "del-lab"})
    lab_id = create_resp.json()["id"]
    delete_resp = await client.delete(f"/api/v1/labs/{lab_id}")
    assert delete_resp.status_code == 200
    get_resp = await client.get(f"/api/v1/labs/{lab_id}")
    assert get_resp.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_lab_not_found(client):
    response = await client.get("/api/v1/labs/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_run_lab(client):
    create_resp = await client.post(
        "/api/v1/labs",
        json={"name": "run-lab"},
    )
    lab_id = create_resp.json()["id"]
    response = await client.post(f"/api/v1/labs/{lab_id}/run")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ("running", "success", "pending")
