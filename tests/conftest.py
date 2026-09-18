import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def db_url(tmp_dir):
    """Provide a SQLite database URL in temp directory."""
    db_path = tmp_dir / "test.db"
    return f"sqlite:///{db_path}"

@pytest.fixture
def database_manager(db_url):
    """Provide a DatabaseManager with a temp database."""
    from kernellab.persistence.database import DatabaseManager
    dm = DatabaseManager(database_url=db_url)
    dm.create_tables()
    return dm

@pytest.fixture
def lab_service(database_manager):
    """Provide a LabService instance."""
    from kernellab.application.lab_service import LabService
    from kernellab.persistence.repositories import LabRepository
    repo = LabRepository(database_manager)
    return LabService(repo)

@pytest.fixture
def job_service(database_manager):
    """Provide a JobService instance."""
    from kernellab.application.job_service import JobService
    from kernellab.persistence.repositories import JobRepository
    repo = JobRepository(database_manager)
    return JobService(repo)

@pytest.fixture
def fake_provider():
    """Provide a FakeProvider instance."""
    from kernellab.providers.fake import FakeProvider
    return FakeProvider()

@pytest.fixture
def provider_registry():
    """Provide a ProviderRegistry with FakeProvider registered."""
    from kernellab.providers.fake import FakeProvider
    from kernellab.providers.registry import ProviderRegistry
    registry = ProviderRegistry()
    registry.register("fake", FakeProvider)
    return registry

@pytest.fixture
def sample_config(tmp_dir):
    """Create a sample kernellab.yaml in tmp_dir."""
    config_content = """version: 1
name: test-lab
description: Test laboratory
provider: fake
machine:
  architecture: x86_64
  cpus: 2
  memory: 2G
  disk: 10G
kernel:
  version: "6.12"
  cmdline: "console=ttyS0"
workspace:
  source: ./src
tests:
  - name: test-echo
    command: echo hello
"""
    config_path = tmp_dir / "kernellab.yaml"
    config_path.write_text(config_content)
    return str(config_path)
