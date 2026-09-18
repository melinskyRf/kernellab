# Kernel Lab

<p align="center">
  <strong>A reproducible laboratory for kernel and driver development.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#cli-commands">CLI</a> •
  <a href="#api-reference">API</a> •
  <a href="#development">Development</a> •
  <a href="https://github.com/melinskyRf/kernellab/blob/main/docs/roadmap.md">Roadmap</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/version-0.1.0-green.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/status-Phase%201-yellow.svg" alt="Status">
</p>

---

> ⚠️ **Kernel Lab is currently under development.** This release (Phase 1) provides the architectural foundation with a FakeProvider that simulates operations. Real virtual machine integration (QEMU/KVM) is planned for Phase 2.

---

## Why Kernel Lab?

Kernel and driver development is powerful — but the tooling around it is fragmented. Developers today must manually orchestrate a dozen different tools just to test a single kernel module:

```mermaid
graph LR
    subgraph "Current Workflow"
        QEMU["QEMU/KVM"] --> Scripts["Shell Scripts"]
        Scripts --> SSH["SSH Access"]
        SSH --> Dmesg["dmesg Capture"]
        Dmesg --> Logs["Log Files"]
        Logs --> Snapshots["Manual Snapshots"]
        Snapshots --> Cleanup["Manual Cleanup"]
    end
    
    style QEMU fill:#FF5722,color:#fff
    style Scripts fill:#FF9800,color:#fff
    style SSH fill:#FFC107,color:#000
    style Dmesg fill:#8BC34A,color:#fff
    style Logs fill:#4CAF50,color:#fff
    style Snapshots fill:#009688,color:#fff
    style Cleanup fill:#607D8B,color:#fff
```

**The pain is real:**

| Scenario | Today | With Kernel Lab |
|----------|-------|-----------------|
| Test a driver that might crash | Manually create VM, configure, boot, copy module, hope for the best | `kernellab lab run` — disposable VM, automatic recovery |
| Test across kernel versions | Create 3+ VMs manually, maintain each | Single `kernellab.yaml` config, run against multiple kernels |
| Share setup with teammate | Zip VM image + 10-page README | Share `kernellab.yaml` — one command to reproduce |
| Debug kernel panic | Rebuild VM, reconfigure serial console, lose previous state | Snapshots + automatic log capture |
| CI/CD for kernel modules | Custom scripts, fragile, hard to maintain | Native API + GitHub Actions integration |

**Kernel Lab solves this** by providing a single interface that orchestrates virtualization, kernel management, testing, and observability — all driven by a simple YAML configuration.

---

## What Kernel Lab Does

```mermaid
graph TB
    subgraph "Input"
        YAML["kernellab.yaml"]
    end
    
    subgraph "Kernel Lab Engine"
        Config["Configuration Parser"]
        Runtime["Runtime Engine"]
        Provider["Provider System"]
        Logs["Log Collector"]
    end
    
    subgraph "Output"
        Results["Test Results"]
        Artifacts["Artifacts"]
        Reports["Logs & Reports"]
    end
    
    YAML --> Config
    Config --> Runtime
    Runtime --> Provider
    Provider --> Results
    Provider --> Artifacts
    Runtime --> Logs
    Logs --> Reports
    
    style YAML fill:#2196F3,color:#fff
    style Runtime fill:#4CAF50,color:#fff
    style Provider fill:#FF9800,color:#fff
    style Results fill:#9C27B0,color:#fff
```

One command does everything:

```bash
kernellab lab run my-driver-lab
```

This single command will (in future phases):

1. **Parse** your `kernellab.yaml` configuration
2. **Create** a disposable virtual machine
3. **Boot** the specified kernel version
4. **Copy** your modules into the VM
5. **Execute** your test suite
6. **Capture** console output and dmesg
7. **Detect** kernel panics or failures
8. **Save** artifacts and logs
9. **Destroy** the environment (or keep it for debugging)

---

## Example Configuration

```yaml
version: 1
name: my-driver
description: Test environment for my custom driver

provider: qemu

machine:
  architecture: x86_64
  cpus: 4
  memory: 4G
  disk: 20G

kernel:
  version: "6.12"
  cmdline: "console=ttyS0 nokaslr"

workspace:
  source: ./src

tests:
  - name: load-module
    command: insmod my_driver.ko

  - name: verify-loaded
    command: lsmod | grep my_driver

  - name: check-dmesg
    command: dmesg | tail -100

  - name: run-functional-tests
    command: ./run-tests.sh

provider_options:
  timeout: 300
  fail_on_panic: true
```

This configuration is **self-documenting** and **reproducible** — anyone on your team can run the exact same test environment with a single command.

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| **CLI** | ✅ Available | Full command-line interface with Typer + Rich |
| **REST API** | ✅ Available | FastAPI-based API with auto-generated docs |
| **Lab Configuration** | ✅ Available | YAML-based config with validation |
| **Job System** | ✅ Available | Track and manage test executions |
| **Fake Provider** | ✅ Available | Simulated provider for development/testing |
| **Persistent Logs** | ✅ Available | Logs stored in `.kernellab/logs/` |
| **Provider System** | ✅ Available | Pluggable architecture for VM backends |
| **QEMU/KVM Provider** | 🔜 Planned | Real VM execution via QEMU |
| **Kernel Boot** | 🔜 Planned | Boot custom kernels in VMs |
| **Driver Injection** | 🔜 Planned | Auto-copy `.ko` files to VMs |
| **Snapshot/Restore** | 🔜 Planned | Save and restore VM state |
| **Serial Console** | 🔜 Planned | Direct console access to VMs |
| **Crash Detection** | 🔜 Planned | Automatic kernel panic detection |
| **KUnit Integration** | 🔜 Planned | Run kernel unit tests |
| **kselftest Integration** | 🔜 Planned | Run kernel self-tests |
| **Web Dashboard** | 🔜 Planned | Browser-based management UI |
| **Remote Workers** | 🔜 Planned | Execute across multiple machines |
| **ARM64 Emulation** | 🔜 Planned | Test on different architectures |

---

## Architecture

Kernel Lab follows a clean **layered architecture** with clear separation of concerns:

```mermaid
graph TB
    subgraph "Entry Points"
        CLI["CLI<br/><i>Typer + Rich</i>"]
        API["REST API<br/><i>FastAPI</i>"]
    end
    
    subgraph "Application Layer"
        LS["LabService<br/><i>Lab CRUD</i>"]
        JS["JobService<br/><i>Job Management</i>"]
        RS["RuntimeService<br/><i>Orchestration</i>"]
    end
    
    subgraph "Domain Layer"
        Lab["Lab Model"]
        Job["Job Model"]
        Machine["Machine Config"]
        Kernel["Kernel Config"]
    end
    
    subgraph "Infrastructure"
        PR["ProviderRegistry"]
        FP["FakeProvider"]
        QP["QEMUProvider<br/><i>Phase 2</i>"]
        DB["SQLite +<br/>SQLAlchemy"]
    end
    
    CLI --> LS
    CLI --> JS
    CLI --> RS
    API --> LS
    API --> JS
    API --> RS
    
    LS --> Lab
    JS --> Job
    RS --> PR
    RS --> Job
    
    PR --> FP
    PR --> QP
    
    Lab --> DB
    Job --> DB
    
    style CLI fill:#4CAF50,color:#fff
    style API fill:#2196F3,color:#fff
    style FP fill:#FF9800,color:#fff
    style QP fill:#9E9E9E,color:#fff
    style DB fill:#795548,color:#fff
```

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Layered Architecture** | Clear separation between CLI/API, Services, Domain, and Infrastructure |
| **Provider Abstraction** | Virtualization backend is pluggable — swap QEMU for VirtualBox without changing business logic |
| **Shared Service Layer** | CLI and API use the same services — no duplicated logic |
| **Repository Pattern** | Database access is abstracted behind repositories |
| **Configuration as Code** | Everything defined in `kernellab.yaml` — version controlled, reproducible |

---

### How `kernellab lab run` Works

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Runtime
    participant Jobs
    participant Provider
    
    User->>CLI: kernellab lab run my-lab
    CLI->>Runtime: run_lab(config, lab_id)
    
    Runtime->>Jobs: create_job(lab_id, RUN)
    Jobs-->>Runtime: job_id
    
    Runtime->>Jobs: mark_running(job_id)
    
    Runtime->>Provider: get("fake")
    Provider-->>Runtime: FakeProvider
    
    Runtime->>Provider: create(config)
    Provider-->>Runtime: ✓ Environment created
    
    Runtime->>Provider: start(config)
    Provider-->>Runtime: ✓ Machine started
    
    loop Each Test
        Runtime->>Provider: execute(config, command)
        Provider-->>Runtime: ✓ Test completed
    end
    
    Runtime->>Provider: destroy(config)
    Provider-->>Runtime: ✓ Environment destroyed
    
    Runtime->>Jobs: mark_success(job_id, logs)
    
    Runtime-->>CLI: (job, logs)
    CLI-->>User: Job completed successfully
```

---

### Provider System

The provider system allows Kernel Lab to support multiple virtualization backends:

```mermaid
classDiagram
    class Provider {
        <<abstract>>
        +create(config) ProviderResult
        +start(config) ProviderResult
        +stop(config) ProviderResult
        +destroy(config) ProviderResult
        +execute(config, command) ProviderResult
        +snapshot(config, name) ProviderResult
        +restore(config, snapshot_id) ProviderResult
    }
    
    class FakeProvider {
        +create(config) ProviderResult
        +start(config) ProviderResult
        +execute(config, command) ProviderResult
        +destroy(config) ProviderResult
    }
    
    class QEMUProvider {
        <<Phase 2>>
        +create(config) ProviderResult
        +start(config) ProviderResult
        +execute(config, command) ProviderResult
        +snapshot(config, name) ProviderResult
    }
    
    class ProviderRegistry {
        -providers: Dict
        +register(name, class)
        +get(name) Provider
    }
    
    Provider <|-- FakeProvider
    Provider <|-- QEMUProvider
    ProviderRegistry o-- Provider
```

> **Adding a new provider** is simple: implement the `Provider` abstract class and register it in the `ProviderRegistry`. No other code needs to change.

---

### Data Model

```mermaid
erDiagram
    LAB {
        uuid id PK
        string name UK
        string description
        string provider
        string status
        json configuration
        timestamp created_at
        timestamp updated_at
    }
    
    JOB {
        uuid id PK
        uuid lab_id FK
        string type
        string status
        timestamp created_at
        timestamp started_at
        timestamp finished_at
        int exit_code
        text error
        text logs
    }
    
    LAB ||--o{ JOB : "produces"
    
    note for LAB "Status: created | ready | running | stopped | failed"
    note for JOB "Status: pending | running | success | failed | cancelled"
    note for JOB "Type: CREATE | START | STOP | RUN | TEST | SNAPSHOT | DESTROY"
```

---

## Quick Start

### Prerequisites

- **Python 3.12** or higher
- **pip** or **uv** package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/melinskyRf/kernellab.git
cd kernel-lab

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows

# Install with development dependencies
pip install -e ".[dev]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

### Verify Installation

```bash
$ kernellab --version
Kernel Lab 0.1.0

$ kernellab --help
Usage: kernellab [OPTIONS] COMMAND [ARGS]...

  A reproducible laboratory for kernel and driver development.

Options:
  --version  -v  Show version and exit.
  --help         Show this message and exit.

Commands:
  init     Initialize kernellab.yaml and .kernellab/ directory.
  logs     Show logs for a specific job.
  server   Start the Kernel Lab API server.
  lab      Manage labs.
  job      Manage jobs.
  config   Manage configuration.
```

---

## Your First Lab

Follow these steps to create and run your first lab:

### Step 1: Initialize

```bash
mkdir my-first-lab
cd my-first-lab
kernellab init
```

This creates:

```
my-first-lab/
├── kernellab.yaml      # Configuration file
└── .kernellab/         # Working directory
    ├── logs/           # Job logs
    ├── artifacts/      # Test artifacts
    └── runtime/        # Runtime data
```

### Step 2: Configure

Edit `kernellab.yaml`:

```yaml
version: 1
name: my-first-lab
provider: fake

machine:
  architecture: x86_64
  cpus: 2
  memory: 2G

kernel:
  version: "6.12"

tests:
  - name: hello-test
    command: echo "Hello from Kernel Lab!"
```

### Step 3: Validate

```bash
kernellab config validate
```

### Step 4: Create and Run

```bash
# Create the lab
kernellab lab create my-first-lab

# Run it
kernellab lab run my-first-lab
```

Output:

```
Kernel Lab

Lab: my-first-lab

✓ Environment created
✓ Machine started
✓ Kernel boot simulated
✓ Tests executed
✓ Logs collected

Job completed successfully.

Job ID: 01HXYZ123456...
```

### Step 5: Inspect Results

```bash
# List all jobs
kernellab job list

# View job details
kernellab job show 01HXYZ123456...

# View logs
kernellab logs 01HXYZ123456...
```

---

## CLI Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `kernellab init` | Initialize a new project | `kernellab init` |
| `kernellab --version` | Show version | `kernellab -v` |
| `kernellab server` | Start API server | `kernellab server --port 8000` |

### Lab Management

| Command | Description | Example |
|---------|-------------|---------|
| `kernellab lab create <name>` | Create a new lab | `kernellab lab create driver-test` |
| `kernellab lab list` | List all labs | `kernellab lab list` |
| `kernellab lab show <name>` | Show lab details | `kernellab lab show driver-test` |
| `kernellab lab delete <name>` | Delete a lab | `kernellab lab delete driver-test` |
| `kernellab lab run <name>` | Run a lab | `kernellab lab run driver-test` |

### Job Management

| Command | Description | Example |
|---------|-------------|---------|
| `kernellab job list` | List all jobs | `kernellab job list` |
| `kernellab job show <id>` | Show job details | `kernellab job show 01HXYZ...` |
| `kernellab logs <id>` | View job logs | `kernellab logs 01HXYZ...` |

### Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `kernellab config validate` | Validate config file | `kernellab config validate` |

---

## API Reference

Start the API server:

```bash
kernellab server
```

The server starts at `http://127.0.0.1:8000`.

### Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Endpoints

```mermaid
graph LR
    subgraph "Health"
        H["GET /health"]
    end
    
    subgraph "Labs"
        L1["POST /api/v1/labs"]
        L2["GET /api/v1/labs"]
        L3["GET /api/v1/labs/{id}"]
        L4["DELETE /api/v1/labs/{id}"]
        L5["POST /api/v1/labs/{id}/run"]
    end
    
    subgraph "Jobs"
        J1["GET /api/v1/jobs"]
        J2["GET /api/v1/jobs/{id}"]
        J3["GET /api/v1/jobs/{id}/logs"]
    end
    
    style H fill:#4CAF50,color:#fff
    style L1 fill:#2196F3,color:#fff
    style L2 fill:#2196F3,color:#fff
    style L3 fill:#2196F3,color:#fff
    style L4 fill:#f44336,color:#fff
    style L5 fill:#FF9800,color:#fff
    style J1 fill:#9C27B0,color:#fff
    style J2 fill:#9C27B0,color:#fff
    style J3 fill:#9C27B0,color:#fff
```

### Example Requests

```bash
# Health check
curl http://127.0.0.1:8000/health
# → {"status": "ok", "service": "kernellab"}

# Create a lab
curl -X POST http://127.0.0.1:8000/api/v1/labs \
  -H "Content-Type: application/json" \
  -d '{"name": "my-lab", "provider": "fake"}'

# List all labs
curl http://127.0.0.1:8000/api/v1/labs

# Run a lab
curl -X POST http://127.0.0.1:8000/api/v1/labs/{lab_id}/run

# Get job logs
curl http://127.0.0.1:8000/api/v1/jobs/{job_id}/logs
```

---

## Development

### Project Structure

```
kernel-lab/
├── src/kernellab/           # Source code
│   ├── cli/                 # CLI commands (Typer)
│   ├── api/                 # REST API (FastAPI)
│   ├── domain/              # Domain models
│   ├── application/         # Application services
│   ├── providers/           # Provider system
│   ├── persistence/         # Database layer
│   ├── config/              # Configuration
│   └── schemas/             # Pydantic schemas
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # API tests
│   └── cli/                 # CLI tests
├── docs/                    # Documentation
│   └── diagrams/            # Mermaid diagrams
└── examples/                # Example configurations
```

### Available Commands

```bash
make install      # Install with dev dependencies
make test         # Run all tests
make test-cov     # Run tests with coverage
make lint         # Check code style (ruff)
make format       # Format code (ruff)
make typecheck    # Run type checks (mypy)
make run          # Start API server
make clean        # Remove build artifacts
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v    # API integration tests
pytest tests/cli/ -v            # CLI tests

# Run with coverage
make test-cov
```

### Code Quality

```bash
# Linting
make lint

# Auto-fix lint issues
ruff check --fix src/ tests/

# Formatting
make format

# Type checking
make typecheck
```

### Database

Kernel Lab uses SQLite for persistence. The database is stored at `.kernellab/kernellab.db`.

To reset the database:

```bash
rm .kernellab/kernellab.db
kernellab init  # Recreates the database
```

---

## Docker

> ⚠️ **Docker is for API development only.** Containers share the host kernel and are **not** the isolation mechanism for Kernel Lab. Real kernel isolation requires virtualization (QEMU/KVM) in future phases.

```bash
# Start the API server in Docker
docker compose up

# Or build and run
docker build -t kernellab .
docker run -p 8000:8000 kernellab
```

---

## Security Considerations

Kernel code and drivers can be dangerous. They can:

- **Kernel panic** — crash the entire system
- **Memory corruption** — corrupt data across processes
- **Deadlocks** — hang the system indefinitely
- **Network disruption** — bring down network interfaces
- **Filesystem corruption** — destroy data permanently

**Kernel Lab executes potentially dangerous code inside disposable virtual machines.** In future phases, all test execution happens in isolated VMs that are destroyed after each run.

> ⚠️ **Never run untrusted kernel modules directly on your host machine.** Always use Kernel Lab's isolated environments.

---

## Project Principles

| Principle | Description |
|-----------|-------------|
| **Reproducible** | Same `kernellab.yaml` produces identical environment every time |
| **Disposable** | VMs are created and destroyed — no state to manage |
| **Observable** | Every operation generates logs and artifacts |
| **Automatable** | All operations scriptable via CLI or API |
| **Provider-independent** | No lock-in to QEMU, VirtualBox, or any specific tool |
| **Developer-friendly** | Simple commands, clear errors, fast feedback loops |
| **Safe by default** | Destructive operations require explicit confirmation |

---

## What Kernel Lab Is NOT

Kernel Lab **does not replace** the tools you already use. It **orchestrates** them:

| Tool | Relationship |
|------|--------------|
| **QEMU/KVM** | Kernel Lab manages VM lifecycle |
| **VirtualBox** | Kernel Lab can use it as a backend |
| **KUnit** | Kernel Lab can run and collect results |
| **kselftest** | Kernel Lab can integrate test suites |
| **Linux** | Kernel Lab runs on Linux (and others) |

Kernel Lab is a layer of **orchestration**, **automation**, and **observability** on top of existing technologies — not a replacement for them.

---

## Roadmap

The full roadmap is available in [docs/roadmap.md](docs/roadmap.md).

**Current Status: Phase 1 — Foundation ✅**

- [x] Project architecture
- [x] CLI with Typer + Rich
- [x] REST API with FastAPI
- [x] Domain models
- [x] Application services
- [x] Provider system with FakeProvider
- [x] SQLite persistence
- [x] Configuration system
- [x] Comprehensive test suite (58 tests)
- [x] Documentation and diagrams

**Next: Phase 2 — QEMU Runtime**

- [ ] QEMU/KVM integration
- [ ] VM lifecycle management
- [ ] Kernel boot
- [ ] Serial console
- [ ] SSH communication

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

---

## License

This project is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for the Linux kernel community.
</p>
