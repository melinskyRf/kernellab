# Core Concepts

This document explains the key concepts and domain model of Kernel Lab.

## Lab

A **Lab** is the central entity in Kernel Lab. It represents a named, reproducible environment for kernel and driver testing.

**Properties:**
- `name` — Unique identifier (e.g., `my-driver-test`)
- `provider` — Virtualization backend to use (e.g., `fake`, `qemu`)
- `machine` — Hardware configuration (CPUs, memory, architecture)
- `kernel` — Kernel version and configuration
- `tests` — List of test commands to execute
- `status` — Current state (`created`, `running`, `completed`, `failed`)

**Lifecycle:**
1. Create a lab from configuration
2. The lab is registered in the system
3. Execute the lab (`lab run`)
4. The provider creates a VM, boots the kernel, runs tests
5. Results and artifacts are collected
6. The VM is destroyed

## Machine

A **Machine** defines the virtual hardware configuration for a lab run.

**Properties:**
- `architecture` — CPU architecture (`x86_64`, `arm64`)
- `cpus` — Number of virtual CPUs
- `memory` — Amount of RAM (e.g., `4G`, `2G`)
- `disk` — Disk size (e.g., `20G`)
- `machine_type` — QEMU machine type (e.g., `q35`, `virt`)

**Example:**
```yaml
machine:
  architecture: x86_64
  cpus: 4
  memory: 4G
  disk: 20G
```

## Kernel

A **Kernel** represents the Linux kernel version and configuration to use in a lab.

**Properties:**
- `version` — Kernel version string (e.g., `6.12`, `6.6`)
- `source` — Where to obtain the kernel (`download`, `local`, `git`)
- `config` — Kernel configuration (e.g., `defconfig`, `custom`)
- `modules` — Additional kernel modules to compile and inject

**Example:**
```yaml
kernel:
  version: "6.12"
  config: defconfig
  modules:
    - name: my_driver
      path: ./drivers/my_driver
```

## Job

A **Job** represents a single execution of a lab run. Each `lab run` creates a new job.

**Properties:**
- `id` — Unique job identifier (UUID)
- `lab_id` — Reference to the lab
- `type` — Job type (`run`, `test`, `destroy`)
- `status` — Current state (`pending`, `running`, `completed`, `failed`, `cancelled`)
- `created_at` — When the job was created
- `started_at` — When execution began
- `completed_at` — When execution finished
- `artifacts` — Files produced by the job
- `logs` — Console output and log messages
- `error` — Error message if the job failed

**Status Transitions:**
```
pending → running → completed
                  → failed
                  → cancelled
```

## Provider

A **Provider** is a virtualization backend that implements VM lifecycle operations. Providers are pluggable — Kernel Lab supports multiple backends.

**Interface:**
- `create_vm(config)` — Create a new virtual machine
- `boot_kernel(kernel_config)` — Boot a kernel in the VM
- `wait_for_ready(timeout)` — Wait for the guest to be ready
- `execute_command(command)` — Run a command in the guest
- `collect_artifacts(output_dir)` — Collect files from the guest
- `destroy_vm(vm_id)` — Destroy the virtual machine
- `get_console_output()` — Retrieve console output

**Available Providers:**
- `FakeProvider` — Simulates VM operations (Phase 1, development)
- `QemuProvider` — Real QEMU/KVM integration (Phase 2)

## Artifact

An **Artifact** is a file or output produced by a job. Artifacts are saved for inspection and debugging.

**Types:**
- Console output (serial log)
- dmesg output
- Test results
- Kernel logs
- Core dumps
- Custom files collected from the VM

**Storage:**
- Stored in `workspace/artifacts/<job-id>/`
- Referenced by job in the database
- Can be downloaded via API

## Snapshot

A **Snapshot** captures the state of a VM at a point in time. Snapshots enable:

- **Recovery** — Restore to a known good state after a crash
- **Debugging** — Inspect VM state after a failure
- **Branching** — Create multiple test paths from a common state

**Operations:**
- `create` — Save current VM state
- `list` — List available snapshots
- `restore` — Revert to a snapshot
- `delete` — Remove a snapshot

**Note:** Snapshots are not yet implemented in Phase 1. They will be available in Phase 4 with QEMU's built-in snapshot support.

## Test

A **Test** is a command to execute inside the guest VM during a lab run. Tests are defined in the lab configuration and executed sequentially.

**Properties:**
- `name` — Test identifier
- `command` — Shell command to execute
- `timeout` — Maximum execution time
- `expected_exit_code` — Expected return code (default: 0)
- `success_patterns` — Regex patterns indicating success
- `failure_patterns` — Regex patterns indicating failure

**Example:**
```yaml
tests:
  - name: load-driver
    command: insmod /lib/modules/my_driver.ko
    timeout: 10s

  - name: verify-loaded
    command: lsmod | grep my_driver
    expected_exit_code: 0

  - name: check-dmesg
    command: dmesg | tail -100
    failure_patterns:
      - "BUG:"
      - "Oops:"
      - "panic"
```

## Runtime

The **Runtime** manages the lifecycle of VMs during a lab run. It coordinates between the application layer and the provider.

**Responsibilities:**
- Select the appropriate provider
- Create and configure VMs
- Execute the test sequence
- Handle timeouts and failures
- Collect artifacts and logs
- Clean up resources

## Workspace

A **Workspace** is a directory containing a Kernel Lab project. It holds:

- `kernellab.yaml` — Lab configuration
- `artifacts/` — Job outputs and logs
- `.kernellab/` — Internal state (database, cache)

**Structure:**
```
my-lab/
├── kernellab.yaml
├── artifacts/
│   └── <job-id>/
│       ├── console.log
│       ├── dmesg.log
│       └── test-results.json
├── .kernellab/
│   └── kernellab.db
└── kernels/          # Downloaded kernels (cached)
```

## Configuration

The **Configuration** (`kernellab.yaml`) defines everything needed to run a lab:

```yaml
version: 1
name: my-lab
provider: qemu

machine:
  architecture: x86_64
  cpus: 4
  memory: 4G

kernel:
  version: "6.12"
  config: defconfig

tests:
  - name: smoke-test
    command: echo "Hello from Kernel Lab"
```

Configuration is validated at load time and provides clear error messages for invalid settings.
