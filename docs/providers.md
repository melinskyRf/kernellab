# Providers

Providers are the pluggable virtualization backends in Kernel Lab. Each provider implements a common interface, allowing Kernel Lab to work with different VM technologies.

## Provider Interface

All providers implement the `Provider` protocol:

```python
from typing import Protocol, Any

class Provider(Protocol):
    """Protocol that all providers must implement."""

    name: str

    def create_vm(self, config: MachineConfig) -> dict[str, Any]:
        """Create a new virtual machine.

        Args:
            config: Machine configuration (CPUs, memory, disk, arch).

        Returns:
            Dictionary with VM details (id, name, etc.).
        """
        ...

    def destroy_vm(self, vm_id: str) -> None:
        """Destroy a virtual machine and release all resources.

        Args:
            vm_id: The unique identifier of the VM to destroy.
        """
        ...

    def boot_kernel(self, kernel_config: KernelConfig) -> None:
        """Boot a kernel in the VM.

        Args:
            kernel_config: Kernel version, path, and boot parameters.
        """
        ...

    def wait_for_ready(self, timeout: float = 60.0) -> bool:
        """Wait for the guest to be ready (SSH available, boot complete).

        Args:
            timeout: Maximum seconds to wait.

        Returns:
            True if ready, False if timed out.
        """
        ...

    def execute_command(self, command: str, timeout: float = 30.0) -> tuple[int, str, str]:
        """Execute a command inside the guest.

        Args:
            command: Shell command to run.
            timeout: Maximum seconds for execution.

        Returns:
            Tuple of (exit_code, stdout, stderr).
        """
        ...

    def collect_artifacts(self, output_dir: str) -> list[str]:
        """Collect files from the guest VM.

        Args:
            output_dir: Local directory to save artifacts.

        Returns:
            List of paths to collected artifact files.
        """
        ...

    def get_console_output(self) -> str:
        """Retrieve the full console output from the VM.

        Returns:
            Console output as a string.
        """
        ...
```

## FakeProvider (Phase 1)

The `FakeProvider` simulates all provider operations without creating real VMs. It is used for development and testing of the Kernel Lab infrastructure itself.

**Behavior:**
- `create_vm` — Returns a fake VM ID and configuration
- `boot_kernel` — Logs the kernel configuration
- `wait_for_ready` — Returns `True` immediately
- `execute_command` — Logs the command and returns success
- `collect_artifacts` — Returns an empty list
- `get_console_output` — Returns simulated console output
- `destroy_vm` — No-op

**Use cases:**
- Developing the CLI and API
- Testing the job system
- Running in CI without KVM access
- Quick smoke tests

## QemuProvider (Phase 2 — Future)

The `QemuProvider` will implement real QEMU/KVM integration.

**Implementation Plan:**

```python
class QemuProvider:
    """QEMU/KVM provider for real VM execution."""

    name = "qemu"

    def __init__(self, qemu_binary: str = "qemu-system-x86_64"):
        self.qemu_binary = qemu_binary
        self.process: subprocess.Popen | None = None
        self.vm_id: str | None = None

    def create_vm(self, config: MachineConfig) -> dict[str, Any]:
        """Create QEMU VM process.

        Constructs QEMU command line with:
        - Machine type (q35 for x86_64, virt for ARM)
        - CPU configuration (host passthrough with KVM)
        - Memory allocation
        - Disk image (qcow2 overlay)
        - Network (user-mode with port forwarding)
        - Serial console
        - Kernel and initrd paths
        """
        cmd = [
            self.qemu_binary,
            "-machine", f"{self._machine_type()},accel=kvm",
            "-cpu", "host",
            "-smp", str(config.cpus),
            "-m", config.memory,
            "-kernel", config.kernel_path,
            "-append", config.kernel_args,
            "-drive", f"file={self._overlay_path()},if=virtio,format=qcow2",
            "-serial", "stdio",
            "-nographic",
            "-monitor", "none",
        ]
        # ... start process, return VM details

    def boot_kernel(self, kernel_config: KernelConfig) -> None:
        """Kernel is passed via -kernel flag at VM creation.

        For hot-loading a different kernel, would require
        rebooting the VM or using kexec.
        """
        pass  # Handled in create_vm

    def wait_for_ready(self, timeout: float = 60.0) -> bool:
        """Wait for SSH to become available.

        Uses paramiko or subprocess ssh to test connectivity.
        Retries with exponential backoff.
        """
        # Poll SSH until ready or timeout

    def execute_command(self, command: str, timeout: float = 30.0) -> tuple[int, str, str]:
        """Execute command via SSH.

        Uses paramiko or subprocess ssh.
        Returns (exit_code, stdout, stderr).
        """
        # ssh -p <port> root@localhost "<command>"

    def collect_artifacts(self, output_dir: str) -> list[str]:
        """Copy files from VM via SCP.

        Copies specified paths from guest to local output_dir.
        """
        # scp -P <port> root@localhost:/path/to/artifact output_dir/

    def get_console_output(self) -> str:
        """Return captured serial console output.

        Console output is captured from QEMU's -serial stdio
        and stored in a buffer.
        """
        return self.console_buffer

    def destroy_vm(self, vm_id: str) -> None:
        """Stop QEMU process.

        Sends SIGTERM, waits, then SIGKILL if needed.
        Cleans up overlay images.
        """
        # self.process.terminate()
        # self.process.wait(timeout=10)
        # Remove overlay qcow2
```

### Disk Image Management

```bash
# Base image location
~/.cache/kernellab/images/base-x86_64.qcow2

# Create overlay for each lab run
qemu-img create -f qcow2 \
  -b ~/.cache/kernellab/images/base-x86_64.qcow2 \
  -F qcow2 \
  /tmp/kernellab/<job-id>/overlay.qcow2

# Cleanup after lab run
rm /tmp/kernellab/<job-id>/overlay.qcow2
```

### Serial Console

QEMU's serial console is the primary output channel:

```bash
# QEMU command includes:
-serial stdio     # Output to terminal
# or
-serial file:console.log  # Output to file
# or
-serial tcp:127.0.0.1:4321,server,nowait  # Network access
```

Kernel boot arguments ensure output goes to serial:
```
console=ttyS0,115200n8
```

## VirtualBoxProvider (Future)

A VirtualBox provider could be implemented for environments without KVM:

```python
class VirtualBoxProvider:
    """VirtualBox provider for cross-platform VM execution."""

    name = "virtualbox"

    def create_vm(self, config: MachineConfig) -> dict[str, Any]:
        """Create VM using VBoxManage."""
        # VBoxManage createvm --name <name> --register
        # VBoxManage modifyvm <name> --memory <mem> --cpus <cpus>
        # VBoxManage storagectl <name> --add sata
        # VBoxManage storageattach <name> --medium overlay.vdi

    def boot_kernel(self, kernel_config: KernelConfig) -> None:
        """Boot kernel via VBoxManage.

        VirtualBox doesn't support direct kernel boot like QEMU.
        Would need a bootloader in the disk image or use
        VBoxManage's experimental --kernel flag.
        """
        pass

    # ... other methods
```

## Implementing a Custom Provider

To add a new provider:

1. **Create the provider class:**
```python
# kernellab/providers/my_provider.py
class MyProvider:
    name = "my-provider"

    def create_vm(self, config):
        ...
    # ... implement all interface methods
```

2. **Register it in the factory:**
```python
# kernellab/providers/__init__.py
PROVIDERS = {
    "fake": FakeProvider,
    "qemu": QemuProvider,
    "my-provider": MyProvider,
}
```

3. **Add configuration options:**
```yaml
version: 1
name: my-lab
provider: my-provider

provider_config:
  my-provider:
    custom_option: value
```

No changes to the application layer, CLI, or API are required.
