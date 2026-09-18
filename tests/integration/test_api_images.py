import httpx
import pytest

from kernellab.persistence.database import DatabaseManager


@pytest.fixture
def test_app(db_url, tmp_dir):
    from kernellab.api import dependencies
    from kernellab.api.app import create_app
    from kernellab.images.repository import ImageRepository
    from kernellab.images.service import ImageService

    db = DatabaseManager(database_url=db_url)
    db.create_tables()

    img_repo = ImageRepository(db)
    img_service = ImageService(img_repo)

    def override_get_database_manager():
        yield db

    def override_get_image_service():
        return img_service

    app = create_app()
    app.dependency_overrides[dependencies.get_database_manager] = override_get_database_manager
    app.dependency_overrides[dependencies.get_image_service] = override_get_image_service

    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    transport = httpx.ASGITransport(app=test_app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_images(client):
    response = await client.get("/api/v1/images")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_image(client, tmp_dir):
    img_file = tmp_dir / "test.qcow2"
    img_file.touch()
    response = await client.post(
        "/api/v1/images",
        json={
            "name": "api-test-img",
            "path": str(img_file),
            "provider": "qemu",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "api-test-img"
    assert data["format"] == "qcow2"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_image_not_found(client):
    response = await client.post(
        "/api/v1/images",
        json={
            "name": "bad-img",
            "path": "/nonexistent/file.qcow2",
        },
    )
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_image_duplicate(client, tmp_dir):
    img_file = tmp_dir / "test.qcow2"
    img_file.touch()
    resp1 = await client.post(
        "/api/v1/images",
        json={"name": "dup-img", "path": str(img_file), "provider": "qemu"},
    )
    assert resp1.status_code == 201
    resp2 = await client.post(
        "/api/v1/images",
        json={"name": "dup-img", "path": str(img_file), "provider": "qemu"},
    )
    assert resp2.status_code == 409
