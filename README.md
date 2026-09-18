# Kernel Lab

**A reproducible laboratory for kernel and driver development.**

> ⚠️ **Kernel Lab is currently under development.** Phase 1 uses a FakeProvider and does not yet launch real virtual machines. QEMU/KVM support is planned for Phase 2.

---

## The Problem

Kernel and driver development today requires juggling multiple tools:

- **QEMU/KVM** for virtualization
- **VirtualBox/VMware** for alternative VMs
- **libvirt** for VM management
- **Shell scripts** for automation
- **Cloud images** for base systems
- **SSH** for remote access
- **Serial consoles** for kernel output
- **Snapshot tools** for state management
- **Log collectors** for debugging

Common pain points:

- Recreating a VM after a kernel panic
- Testing multiple kernel versions
- Testing a driver that might crash the system
- Maintaining different disk images
- Configuring networking for VMs
- Copying modules into VMs
- Capturing dmesg output
- Reproducing a setup on another machine
- Sharing configurations with teammates

This results in **manual setup**, **custom scripts**, **hard-to-reproduce environments**, and **scattered configurations**.

---

## The Vision

```bash
kernellab run
```

Should be sufficient to:

1. Prepare the environment
2. Create a VM
3. Select a kernel
4. Boot the kernel
5. Copy modules
6. Execute tests
7. Capture console output
8. Capture dmesg
9. Detect failures
10. Save artifacts
11. Restore snapshots
12. Destroy the environment

---

## Example Configuration

```yaml
version: 1
name: my-driver
provider: qemu

machine:
  architecture: x86_64
  cpus: 4
  memory: 4G

kernel:
  version: "6.12"

tests:
  - name: load-driver
    command: insmod my_driver.ko

  - name: verify
    command: dmesg | tail -100
```

---

## Features

| Feature | Status |
|---|---|
| CLI | ✅ Phase 1 |
| REST API | ✅ Phase 1 |
| Lab configuration | ✅ Phase 1 |
| Job system | ✅ Phase 1 |
| Fake provider | ✅ Phase 1 |
| Persistent logs | ✅ Phase 1 |
| QEMU/KVM provider | 🔜 Planned |
| Kernel boot | 🔜 Planned |
| Driver injection | 🔜 Planned |
| Snapshot/restore | 🔜 Planned |
| Serial console | 🔜 Planned |
| Crash detection | 🔜 Planned |
| KUnit integration | 🔜 Planned |
| kselftest integration | 🔜 Planned |
| Web interface | 🔜 Planned |
| Remote workers | 🔜 Planned |
| ARM64 emulation | 🔜 Planned |

---

## Architecture

```
                    ┌─────────────────────┐
                    │      Kernel Lab     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
             CLI             API             SDK
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Application Layer   │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
       Lab Service        Job Service       Runtime Service
                                                   │
                                                   ▼
                                         Provider Interface
                                                   │
                    ┌──────────────────────────────┼──────────────┐
                    │                              │              │
                    ▼                              ▼              ▼
               FakeProvider                    QEMU           VirtualBox
                  (Phase 1)                   (Phase 2)       (Future)
```

---

## Quick Start

### Prerequisites

- Python 3.12+

### Installation

```bash
git clone https://github.com/kernellab/kernellab.git
cd kernel-lab
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

Install:

```bash
pip install -e ".[dev]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

### Verify Installation

```bash
kernellab --version
# Kernel Lab 0.1.0

kernellab --help
```

---

## Your First Lab

```bash
mkdir hello-lab && cd hello-lab

# Initialize Kernel Lab in current directory
kernellab init

# Validate configuration
kernellab config validate

# Create a lab
kernellab lab create hello-lab

# List labs
kernellab lab list

# Run the lab (simulated with FakeProvider)
kernellab lab run hello-lab

# View jobs
kernellab job list

# View logs for a specific job
kernellab logs <job-id>
```

---

## API Server

Start the API server:

```bash
kernellab server
```

The server starts at `http://127.0.0.1:8000`.

Interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Example API Calls

```bash
# Health check
curl http://127.0.0.1:8000/health

# Create a lab
curl -X POST http://127.0.0.1:8000/api/v1/labs \
  -H "Content-Type: application/json" \
  -d '{"name": "my-lab", "provider": "fake"}'

# List labs
curl http://127.0.0.1:8000/api/v1/labs
```

---

## Docker (Development Only)

> ⚠️ Docker is used **only** for API development in Phase 1. Containers share the host kernel and are **not** the isolation mechanism for Kernel Lab. Real kernel isolation requires virtualization (QEMU/KVM) in Phase 2.

```bash
docker compose up
```

---

## Development

### Setup

```bash
git clone https://github.com/kernellab/kernellab.git
cd kernel-lab
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Available Commands

```bash
make install    # Install project with dev dependencies
make dev        # Same as install
make test       # Run tests
make lint       # Run linter
make format     # Format code
make typecheck  # Run type checker
make run        # Start API server
make clean      # Clean build artifacts
```

### Running Tests

```bash
make test
# or
pytest tests/ -v
```

### Code Quality

```bash
make lint       # ruff check
make format     # ruff format
make typecheck  # mypy
```

---

## Roadmap

### Phase 1 — Foundation ✅

- Project architecture
- CLI with Typer
- REST API with FastAPI
- Lab model and configuration
- Job system
- SQLite persistence
- Logging system
- FakeProvider for development
- Comprehensive test suite

### Phase 2 — QEMU Runtime

- QEMU/KVM integration
- VM lifecycle management
- Disk image management
- Serial console
- Kernel boot
- SSH communication
- Command execution in VMs

### Phase 3 — Kernel & Driver Workflow

- Kernel download and compilation
- Kernel configuration management
- Module compilation
- Module injection into VMs
- Driver testing automation
- Artifact collection
- dmesg collection

### Phase 4 — Recovery & Automation

- Snapshots and restore
- Kernel panic detection
- Timeout handling
- Automatic recovery
- Test matrix execution
- Parallel jobs

### Phase 5 — Testing Ecosystem

- KUnit integration
- kselftest integration
- LTP integration
- Custom test runners
- CI/CD integration
- GitHub Actions support

### Phase 6 — Web Platform

- Dashboard
- Live console
- Job history
- Artifact browser
- Test results viewer
- Environment management UI

### Phase 7 — Distributed Kernel Lab

- Remote workers
- Multi-host execution
- ARM64 workers
- Bare-metal nodes
- Cloud runners
- Team collaboration

---

## Future: Test Matrix

```yaml
matrix:
  kernel:
    - "6.6"
    - "6.12"
    - "latest"
  architecture:
    - x86_64
    - arm64
```

Would execute across all combinations automatically.

---

## Future: Driver Testing Workflow

```bash
kernellab driver test ./my_driver.ko
```

Pipeline:

1. Create VM
2. Boot kernel
3. Wait for guest
4. Copy `.ko` file
5. `insmod` module
6. Collect dmesg
7. Run tests
8. Remove module
9. Collect results
10. Destroy VM

---

## Security

Kernel Lab is designed for isolated environments. Kernel code and drivers can:

- Cause kernel panics
- Crash the system
- Corrupt memory
- Cause deadlocks
- Bring down network interfaces
- Cause filesystem corruption

In future phases, Kernel Lab will execute this code inside disposable virtual machines. **Never run untrusted kernel modules directly on your host.**

---

## Project Principles

| Principle | Description |
|---|---|
| **Reproducible** | Same configuration produces same environment |
| **Disposable** | Environments can be destroyed and recreated instantly |
| **Observable** | All operations produce logs and artifacts |
| **Automatable** | Every operation can be scripted and chained |
| **Provider-independent** | No lock-in to specific virtualization technology |
| **Developer-friendly** | Simple CLI, clear errors, fast feedback |
| **Safe by default** | Destructive operations require explicit action |

---

## What Kernel Lab Is NOT

Kernel Lab does **not** aim to replace:

- **QEMU/KVM** — Kernel Lab orchestrates them
- **VirtualBox** — Kernel Lab can manage VMs through it
- **Linux** — Kernel Lab runs on Linux (and potentially other OSes)
- **KUnit/kselftest** — Kernel Lab can integrate and run them

Kernel Lab is a layer of:

- **Orchestration**
- **Automation**
- **Configuration**
- **Observability**
- **Reproducibility**

...on top of existing technologies.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
