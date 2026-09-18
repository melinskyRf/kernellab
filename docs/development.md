# Development Guide

This document covers development setup, workflow, and tooling for Kernel Lab.

## Prerequisites

- Python 3.12+
- Git
- Make (optional, for convenience commands)
- [uv](https://docs.astral.sh/uv/) (optional, for fast dependency management)

## Setup

### Clone and Install

```bash
git clone https://github.com/kernellab/kernellab.git
cd kernel-lab
```

### Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### Install Dependencies

With pip:
```bash
pip install -e ".[dev]"
```

With uv:
```bash
uv sync
```

### Verify

```bash
kernellab --version
kernellab --help
```

## Project Structure

```
kernel-lab/
├── src/
│   └── kernellab/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/              # CLI commands
│       │   ├── __init__.py
│       │   ├── app.py        # Typer app
│       │   ├── lab.py        # lab commands
│       │   ├── job.py        # job commands
│       │   └── config.py     # config commands
│       ├── api/              # REST API
│       │   ├── __init__.py
│       │   ├── app.py        # FastAPI app
│       │   ├── routes/       # API routes
│       │   └── models/       # Pydantic models
│       ├── domain/           # Domain models
│       │   ├── __init__.py
│       │   ├── lab.py
│       │   ├── job.py
│       │   ├── provider.py
│       │   └── artifact.py
│       ├── application/      # Application services
│       │   ├── __init__.py
│       │   ├── lab_service.py
│       │   ├── job_service.py
│       │   └── runtime_service.py
│       ├── providers/        # Provider implementations
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── fake.py
│       │   └── qemu.py       # Phase 2
│       ├── persistence/      # Database layer
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── models.py
│       │   └── repositories.py
│       └── config.py         # Configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── examples/
├── scripts/
├── docker/
├── Makefile
├── pyproject.toml
└── README.md
```

## Running the Application

### CLI

```bash
kernellab --help
kernellab lab list
kernellab job list
kernellab server
```

### API Server

```bash
kernellab server
# or
uvicorn kernellab.api.app:app --reload
```

Server starts at `http://127.0.0.1:8000`.

## Testing

### Run All Tests

```bash
make test
# or
pytest tests/ -v
```

### Run Specific Tests

```bash
# Run a specific file
pytest tests/unit/test_lab_service.py -v

# Run a specific test
pytest tests/unit/test_lab_service.py::test_create_lab -v

# Run with coverage
pytest tests/ --cov=kernellab --cov-report=html
```

### Test Structure

```
tests/
├── unit/                  # Unit tests (no I/O, fast)
│   ├── test_domain.py
│   ├── test_lab_service.py
│   └── test_job_service.py
├── integration/           # Integration tests (database, API)
│   ├── test_api.py
│   └── test_database.py
└── fixtures/              # Shared test fixtures
    └── conftest.py
```

## Code Quality

### Linting

```bash
make lint
# or
ruff check src/ tests/
```

### Formatting

```bash
make format
# or
ruff format src/ tests/
```

### Type Checking

```bash
make typecheck
# or
mypy src/kernellab/
```

### All Checks

```bash
make lint && make typecheck && make test
```

## Database

### Location

SQLite database is stored at `.kernellab/kernellab.db` within the workspace.

### Schema

Tables:
- `labs` — Lab configurations
- `jobs` — Job execution records
- `artifacts` — Output files
- `logs` — Log entries

### Migrations

Phase 1 uses direct table creation. Future phases will use Alembic for migrations.

```python
# Create tables (Phase 1)
from kernellab.persistence.database import init_db
init_db()
```

### Manual Inspection

```bash
sqlite3 .kernellab/kernellab.db
.tables
.schema labs
SELECT * FROM labs;
SELECT * FROM jobs;
```

## Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install project with dev dependencies |
| `make dev` | Same as install |
| `make test` | Run test suite |
| `make lint` | Run ruff linter |
| `make format` | Format code with ruff |
| `make typecheck` | Run mypy type checker |
| `make run` | Start API server |
| `make clean` | Clean build artifacts |

## Docker

Docker is available for API development only.

```bash
docker compose up
```

This starts the API server in a container. Note that Docker containers share the host kernel and are **not** the isolation mechanism for Kernel Lab's VM operations.

## Common Workflows

### Adding a New CLI Command

1. Create command file in `src/kernellab/cli/`
2. Add command to the Typer app in `src/kernellab/cli/app.py`
3. Add tests in `tests/unit/`
4. Update `--help` documentation

### Adding a New API Endpoint

1. Create route file in `src/kernellab/api/routes/`
2. Add Pydantic models in `src/kernellab/api/models/`
3. Register router in `src/kernellab/api/app.py`
4. Add tests in `tests/integration/`
5. API docs auto-generate at `/docs`

### Adding a New Domain Model

1. Add model class in `src/kernellab/domain/`
2. Add database model in `src/kernellab/persistence/models.py`
3. Add repository in `src/kernellab/persistence/repositories.py`
4. Add service methods in `src/kernellab/application/`
5. Add tests

### Adding a New Provider

See [docs/providers.md](providers.md) for the provider interface and implementation guide.

## IDE Configuration

### VS Code

Recommended extensions:
- Python
- Pylance
- Ruff
- MyPy

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": false,
  "python.analysis.typeCheckingMode": "strict",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

## Troubleshooting

### Import errors

Ensure the virtual environment is activated and the package is installed in editable mode:
```bash
pip install -e ".[dev]"
```

### Database errors

Delete the database and let it recreate:
```bash
rm .kernellab/kernellab.db
kernellab lab list  # Recreates database
```

### Type errors

Run mypy to check types:
```bash
mypy src/kernellab/ --ignore-missing-imports
```
