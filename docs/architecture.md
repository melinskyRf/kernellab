# Architecture

Kernel Lab follows a layered architecture with clear separation of concerns. Each layer has specific responsibilities and communicates with adjacent layers through well-defined interfaces.

---

## Layers

### Domain Layer

The domain layer contains core business entities and rules. It has no dependencies on frameworks, databases, or external services.

**Responsibilities:**
- Define core models: Lab, Machine, Kernel, Job, Artifact, Snapshot
- Define value objects and enums
- Encode business rules (e.g., a job can only be in valid state transitions)
- Define repository interfaces (not implementations)

**Key types:**
- `Lab` — Top-level container representing a configuration and its runtime state
- `Machine` — Virtual machine specification (architecture, CPUs, memory)
- `Kernel` — Kernel version and configuration
- `Job` — A unit of work (create, run, destroy, test)
- `Artifact` — Output from a job (logs, kernel images, test results)
- `Snapshot` — Saved VM state for restore operations
- `Provider` — Abstract interface for virtualization backends

**Dependencies:** None (pure Python)

---

### Application Layer

The application layer orchestrates domain objects to fulfill use cases. It coordinates between the domain, persistence, and provider layers.

**Responsibilities:**
- Implement use cases (create lab, run lab, stop lab)
- Coordinate domain services
- Manage transactions
- Handle events and notifications
- Validate inputs

**Key services:**
- `LabService` — CRUD operations on labs, validation, state management
- `JobService` — Create, execute, track, and cancel jobs
- `RuntimeService` — Orchestrates provider interactions for lifecycle operations

**Dependencies:** Domain layer, Persistence layer, Provider layer

---

### Provider Layer

The provider layer abstracts virtualization technologies. It defines a common interface that different backends implement.

**Responsibilities:**
- Define the `Provider` protocol/interface
- Implement provider-specific logic
- Manage VM lifecycle (create, start, stop, destroy)
- Handle communication with VMs (SSH, serial console)
- Manage disk images and snapshots

**Providers:**
- `FakeProvider` — Simulates VM operations for development and testing (Phase 1)
- `QEMUProvider` — Real QEMU/KVM virtualization (Phase 2)
- `VirtualBoxProvider` — VirtualBox integration (Future)
- `LibvirtProvider` — libvirt-based management (Future)

**Dependencies:** Domain layer

---

### Persistence Layer

The persistence layer handles data storage and retrieval. It isolates the application from specific database technologies.

**Responsibilities:**
- Store and retrieve domain objects
- Handle database migrations
- Manage connection pooling
- Implement repository interfaces from the domain

**Technologies:**
- SQLite via SQLAlchemy (Phase 1)
- PostgreSQL support (Future)

**Key repositories:**
- `LabRepository` — Persist and query labs
- `JobRepository` — Persist and query jobs
- `ArtifactRepository` — Persist and query artifacts
- `LogRepository` — Store and retrieve logs

**Dependencies:** Domain layer

---

### API Layer

The API layer exposes Kernel Lab as an HTTP service. It handles serialization, validation, and HTTP-specific concerns.

**Responsibilities:**
- Define REST API endpoints
- Request validation (Pydantic models)
- Response serialization
- Authentication (Future)
- Rate limiting (Future)
- WebSocket support for live logs (Future)

**Technologies:**
- FastAPI for HTTP framework
- Pydantic for request/response models
- uvicorn for ASGI server

**Dependencies:** Application layer, Domain layer

---

### CLI Layer

The CLI layer provides a command-line interface. It mirrors API functionality for terminal users.

**Responsibilities:**
- Parse command-line arguments
- Execute corresponding application services
- Format output for terminal display
- Handle interactive prompts
- Manage configuration files

**Technologies:**
- Typer for CLI framework
- Rich for terminal formatting
- Click (via Typer) for argument parsing

**Dependencies:** Application layer, Domain layer

---

## Flow Diagram: `kernellab lab run`

```
┌──────────────────────────────────────────────────────────────┐
│                        CLI Layer                             │
│                                                              │
│  kernellab lab run my-driver                                 │
│       │                                                      │
│       ▼                                                      │
│  Parse args → lab name: "my-driver"                          │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│                                                              │
│  LabService.get_lab("my-driver")                            │
│       │                                                      │
│       ▼                                                      │
│  Lab loaded: { name: "my-driver", provider: "fake", ... }   │
│       │                                                      │
│       ▼                                                      │
│  RuntimeService.run_lab(lab)                                 │
│       │                                                      │
│       ├──► Create Job (type=run, status=pending)             │
│       ├──► Persist Job                                       │
│       ├──► Provider.create_vm(lab.machine)                   │
│       ├──► Provider.boot_kernel(lab.kernel)                  │
│       ├──► Execute tests (lab.tests)                         │
│       ├──► Collect artifacts                                 │
│       ├──► Update Job (status=completed)                     │
│       └──► Return results                                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   Provider Layer                              │
│                                                              │
│  FakeProvider.create_vm(machine_spec)                        │
│       │                                                      │
│       ▼                                                      │
│  Simulate VM creation → VM ID                                │
│       │                                                      │
│       ▼                                                      │
│  FakeProvider.boot_kernel(kernel_spec)                       │
│       │                                                      │
│       ▼                                                      │
│  Simulate boot → "Kernel 6.12.0 booting..."                 │
│       │                                                      │
│       ▼                                                      │
│  FakeProvider.execute_command("insmod my_driver.ko")         │
│       │                                                      │
│       ▼                                                      │
│  Simulate output → "Module loaded successfully"             │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   Persistence Layer                           │
│                                                              │
│  JobRepository.update(job)                                   │
│  LogRepository.store(job_id, logs)                           │
│  ArtifactRepository.store(job_id, artifacts)                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                      CLI Layer                               │
│                                                              │
│  Display results:                                            │
│  ✓ Lab "my-driver" completed                                 │
│  ✓ Job: abc-123                                              │
│  ✓ Tests passed: 2/2                                         │
│  ✓ Logs saved to: .kernellab/logs/abc-123.log                │
└──────────────────────────────────────────────────────────────┘
```

---

## Dependency Rules

1. **Dependency flows inward:** CLI → Application → Domain ← Persistence
2. **Domain has no outward dependencies** on infrastructure
3. **Provider layer depends only on Domain** for types
4. **Application layer coordinates** all other layers
5. **Framework choices are isolated** to their respective layers

---

## Data Flow

```
Configuration File (kernellab.yaml)
        │
        ▼
   Lab Model (Domain)
        │
        ├──► Job (created by RuntimeService)
        │        │
        │        ├──► Provider interactions
        │        │        │
        │        │        └──► VM operations
        │        │
        │        ├──► Artifacts
        │        │
        │        └──► Logs
        │
        └──► Persisted to SQLite
```

---

## Future Considerations

- **Event system:** Decouple layers further via domain events
- **CQRS:** Separate read/write models for complex queries
- **Plugin system:** Allow custom providers and test runners
- **gRPC:** Alternative to REST for internal communication
- **Message queue:** Async job execution with Redis/RabbitMQ
