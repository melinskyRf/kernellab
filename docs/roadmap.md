# Roadmap

This document describes the planned evolution of Kernel Lab across seven phases. Each phase builds on the previous one, progressively adding real virtualization, kernel management, and testing capabilities.

---

## Phase 1 — Foundation ✅ (Current)

**Goal:** Establish architecture, CLI, API, and job system with simulated operations.

### Completed

- Project structure and architecture
- CLI with Typer (init, config, lab, job, logs commands)
- REST API with FastAPI (health, labs, jobs endpoints)
- Lab model and YAML configuration
- Job system with state machine
- SQLite persistence via SQLAlchemy
- Structured logging system
- FakeProvider for development
- Test suite with pytest
- Code quality tools (ruff, mypy)

### What's Working

```bash
kernellab init                        # Initialize project
kernellab config validate             # Validate configuration
kernellab lab create my-lab           # Create lab
kernellab lab run my-lab              # Run lab (simulated)
kernellab job list                    # List jobs
kernellab logs <job-id>               # View logs
```

### Limitations

- No real VMs are created
- No actual kernel boot
- No real driver injection
- FakeProvider returns simulated results

---

## Phase 2 — QEMU Runtime

**Goal:** Launch real virtual machines with QEMU/KVM.

### Core VM Management

- `qemu-system-x86_64` and `qemu-system-aarch64` integration
- VM lifecycle: create, start, stop, destroy
- CPU and memory configuration
- Disk image management with qcow2
- Overlay images for disposable VMs

### QEMU Commands

```bash
# Create disk image
qemu-img create -f qcow2 base.qcow2 20G

# Create overlay (disposable)
qemu-img create -f qcow2 -b base.qcow2 -F qcow2 overlay.qcow2

# Launch VM
qemu-system-x86_64 \
  -enable-kvm \
  -m 4G \
  -smp 4 \
  -drive file=overlay.qcow2,format=qcow2 \
  -kernel bzImage \
  -append "console=ttyS0 root=/dev/sda1" \
  -nographic \
  -serial mon:stdio

# Take snapshot
virsh snapshot-create-as vm-name snapshot-name

# Restore snapshot
virsh snapshot-revert vm-name snapshot-name
```

### Disk Image Strategy

```
base.qcow2          # Read-only base image (cloud-init enabled)
    │
    ▼
overlay-<job>.qcow2 # Writeable overlay per job (copy-on-write)
    │
    ▼
Destroyed after job completes
```

### Networking

- User-mode networking (SLIRP) for simple cases
- TAP interfaces for bridged networking
- Port forwarding for SSH access
- virtio-net for high performance

```bash
# User-mode networking
qemu-system-x86_64 -netdev user,id=net0,hostfwd=tcp::2222-:22 ...

# Bridged networking
qemu-system-x86_64 -netdev tap,id=net0,ifname=tap0 ...
```

### libvirt Integration (Future)

```bash
# Define VM
virsh define vm.xml

# Start VM
virsh start vm-name

# Manage snapshots
virsh snapshot-create-as vm-name snap1
virsh snapshot-revert vm-name snap1

# List VMs
virsh list --all
```

### cloud-init

- Automate initial VM setup
- Configure users, SSH keys, packages
- Execute startup scripts
- Mount shared directories

```yaml
# cloud-init configuration
#instance-id: kernel-lab
#hostname: lab-vm
#users:
#  - name: lab
#    sudo: ALL=(ALL) NOPASSWD:ALL
#    ssh_authorized_keys:
#      - ssh-rsa AAAA...
#packages:
#  - build-essential
#  - git
#runcmd:
#  - echo "VM ready" > /tmp/ready
```

### SSH Communication

- Paramiko or asyncssh for SSH connections
- Execute commands in VMs
- Copy files via SCP/SFTP
- Wait for SSH to become available

```python
# Future: SSH into VM
async with SSHClient("127.0.0.1", port=2222) as ssh:
    result = await ssh.run("uname -r")
    await ssh.copy("my_driver.ko", "/tmp/my_driver.ko")
    await ssh.run("sudo insmod /tmp/my_driver.ko")
```

### Serial Console

- Capture kernel output via serial port
- Monitor boot progress
- Detect kernel panic
- Log dmesg output

```bash
# Serial console output
qemu-system-x86_64 -nographic -serial mon:stdio ...

# Capture to file
qemu-system-x86_64 -nographic -serial file:console.log ...
```

### virtio Drivers

- virtio-blk for disk I/O
- virtio-net for networking
- virtio-serial for console
- virtio-scsi for SCSI devices

### Phase 2 Deliverables

- [ ] QEMUProvider implementation
- [ ] VM lifecycle management
- [ ] Disk image creation and management
- [ ] Serial console capture
- [ ] SSH communication
- [ ] Command execution in VMs
- [ ] Basic networking setup
- [ ] Test suite for QEMU operations

---

## Phase 3 — Kernel & Driver Workflow

**Goal:** Automate kernel compilation, module injection, and driver testing.

### Kernel Management

- Download kernel source from kernel.org
- Configure kernel (make menuconfig equivalent)
- Compile kernel (make -j$(nproc))
- Install modules
- Build initramfs/initrd

### Kernel Commands

```bash
# Download kernel
curl -O https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.12.tar.xz

# Configure kernel
make defconfig
make olddefconfig
scripts/config --enable CONFIG_DEBUG_INFO
scripts/config --enable CONFIG_KGDB

# Compile
make -j$(nproc)
make modules

# Install modules to staging area
make modules_install INSTALL_MOD_PATH=../staging

# Build initramfs
mkinitramfs -o ../initrd.img 6.12.0
```

### Kernel Configuration Management

```yaml
kernel:
  version: "6.12"
  config:
    debug_info: true
    kgdb: true
    kasan: false
    kcsan: false
    custom:
      CONFIG_LOCALVERSION: "-kernellab"
      CONFIG_DEBUG_KERNEL: "y"
```

### Module Compilation and Injection

```bash
# Build module against kernel headers
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules

# Copy module to VM
scp my_driver.ko lab@127.0.0.1:/tmp/

# Load module
ssh lab@127.0.0.1 "sudo insmod /tmp/my_driver.ko"

# Verify loaded
ssh lab@127.0.0.1 "lsmod | grep my_driver"

# Unload
ssh lab@127.0.0.1 "sudo rmmod my_driver"
```

### dmesg Collection

```bash
# Capture dmesg
ssh lab@127.0.0.1 "sudo dmesg" > dmesg.log

# Monitor dmesg in real-time
ssh lab@127.0.0.1 "sudo dmesg -w"

# Filter for module
ssh lab@127.0.0.1 "sudo dmesg | grep my_driver"
```

### Artifact Collection

```
artifacts/
├── kernel/
│   ├── bzImage
│   ├── vmlinux
│   └── modules/
├── logs/
│   ├── console.log
│   ├── dmesg.log
│   └── serial.log
├── test-results/
│   ├── kunit.json
│   ├── kselftest.log
│   └── custom-results.json
└── screenshots/
    └── boot-screen.png
```

### Phase 3 Deliverables

- [ ] Kernel download and extraction
- [ ] Kernel configuration management
- [ ] Kernel compilation orchestration
- [ ] Module compilation
- [ ] Module injection into VMs
- [ ] dmesg collection
- [ ] Artifact management
- [ ] Driver testing workflow

---

## Phase 4 — Recovery & Automation

**Goal:** Handle failures gracefully with snapshots, crash detection, and automatic recovery.

### Snapshots

```bash
# Create snapshot before test
virsh snapshot-create-as lab-vm pre-test-snapshot

# Test fails, restore snapshot
virsh snapshot-revert lab-vm pre-test-snapshot

# Delete snapshot after restore
virsh snapshot-delete lab-vm pre-test-snapshot
```

### Snapshot Strategy

```
VM State
    │
    ├─► Pre-boot snapshot
    │       │
    │       ├─► Boot kernel
    │       │       │
    │       │       ├─► Pre-test snapshot
    │       │       │       │
    │       │       │       ├─► Run test
    │       │       │       │       │
    │       │       │       │       ├─► Success → next test
    │       │       │       │       └─► Failure → restore → retry/abort
    │       │       │       │
    │       │       │       └─► Run next test...
    │       │       │
    │       │       └─► Boot failure → restore → try different kernel
    │       │
    │       └─► Destroy
    │
    └─► Cleanup
```

### Kernel Panic Detection

- Monitor serial console for panic signatures
- Parse dmesg for oops/panic messages
- Detect hung tasks
- Identify soft/hard lockups

```
Panic signatures:
- "Kernel panic - not syncing"
- "Oops: " followed by register dump
- "BUG: unable to handle"
- "RIP:" followed by address
- "Call Trace:" (stack trace)
- "hung_task_timeout_secs"
- "soft lockup - CPU stuck"
```

### Timeout Handling

```yaml
timeouts:
  boot: 120s          # Maximum boot time
  ssh_ready: 30s      # SSH connection timeout
  command: 60s        # Single command timeout
  test: 300s          # Test execution timeout
  total: 600s         # Total job timeout
```

### Automatic Recovery

1. **Boot failure** → Restore snapshot → Try different kernel config
2. **SSH timeout** → Restart VM → Retry connection
3. **Test failure** → Capture state → Restore → Log failure
4. **Kernel panic** → Capture dmesg → Restore → Mark as failed
5. **VM hang** → Force shutdown → Restore → Retry

### Test Matrix Execution

```yaml
matrix:
  kernel:
    - "6.6"
    - "6.12"
    - "latest"
  architecture:
    - x86_64
    - arm64
  config:
    - default
    - debug
```

Executes all combinations: 3 kernels × 2 architectures × 2 configs = 12 test runs.

### Parallel Jobs

- Execute independent test combinations concurrently
- Configurable parallelism limit
- Resource-aware scheduling
- Progress tracking across parallel jobs

### Phase 4 Deliverables

- [ ] Snapshot management
- [ ] Kernel panic detection
- [ ] Timeout handling
- [ ] Automatic recovery
- [ ] Test matrix support
- [ ] Parallel job execution

---

## Phase 5 — Testing Ecosystem

**Goal:** Integrate with Linux kernel testing frameworks.

### KUnit Integration

KUnit is the Linux kernel's unit testing framework.

```bash
# Run KUnit tests
./tools/testing/kunit/kunit.py run

# Parse KUnit output
# [PASSED] test_example
# [FAILED] test_other
```

```yaml
tests:
  - name: kunit
    type: kunit
    config:
      suite: lib/kunit
      timeout: 300
```

### kselftest Integration

kselftest is the kernel's self-test framework.

```bash
# Run all kselftests
make -C tools/testing/selftests run_tests

# Run specific test
make -C tools/testing/selftests TARGETS=mm run_tests
```

```yaml
tests:
  - name: kselftest
    type: kselftest
    config:
      targets:
        - mm
        - bpf
      timeout: 600
```

### LTP Integration

Linux Test Project for system-level testing.

```bash
# Run LTP
./runltp -p -l result.log -S skipfile -f syscalls

# Parse results
# PASS: 4521
# FAIL: 3
# BROK: 12
```

```yaml
tests:
  - name: ltp
    type: ltp
    config:
      scenario: syscalls
      timeout: 3600
```

### Custom Test Runners

```yaml
tests:
  - name: my-test
    type: custom
    command: |
      cd /opt/tests
      ./run_tests.sh --kernel-version $(uname -r)
    timeout: 300
    expected_exit_code: 0
```

### CI/CD Integration

- GitHub Actions workflow generation
- GitLab CI pipeline generation
- Jenkinsfile generation
- Container-based CI runners

```yaml
# GitHub Actions example
ci:
  provider: github-actions
  triggers:
    - push
    - pull_request
  matrix:
    kernel: ["6.6", "6.12"]
```

### Phase 5 Deliverables

- [ ] KUnit test runner
- [ ] kselftest runner
- [ ] LTP runner
- [ ] Custom test runners
- [ ] CI/CD integration
- [ ] Test result aggregation

---

## Phase 6 — Web Platform

**Goal:** Provide a web-based interface for managing Kernel Lab.

### Dashboard

- Overview of running labs
- Job status and history
- System resource usage
- Quick actions

### Live Console

- WebSocket-based live console output
- Serial console streaming
- dmesg monitoring
- Real-time test progress

### Job History

- Complete job history with filters
- Job comparison
- Artifact download
- Log viewing

### Artifact Browser

- Browse collected artifacts
- Download kernel images, logs, test results
- Compare artifacts across jobs
- Artifact retention management

### Test Results Viewer

- Test result visualization
- Pass/fail trends
- Regression detection
- Test coverage (if available)

### Environment Management UI

- Create/edit/delete labs
- Configure machine and kernel settings
- Manage disk images
- VM control (start/stop/snapshot)

### Phase 6 Deliverables

- [ ] Web dashboard
- [ ] Live console via WebSocket
- [ ] Job history and search
- [ ] Artifact browser
- [ ] Test results visualization
- [ ] Environment management UI

---

## Phase 7 — Distributed Kernel Lab

**Goal:** Execute across multiple machines and architectures.

### Remote Workers

- Register remote machines as workers
- Distribute jobs across workers
- Worker health monitoring
- Automatic failover

### Multi-Host Execution

- Execute test matrix across hosts
- Aggregate results from multiple hosts
- Cross-host comparison
- Centralized logging

### ARM64 Workers

- QEMU user-mode emulation
- Native ARM64 hardware
- Cross-compilation support
- Architecture-specific testing

### Bare-Metal Nodes

- Direct hardware access
- Performance testing
- Real hardware quirks
- BMC/IPMI integration

### Cloud Runners

- AWS EC2 instances
- GCP Compute Engine
- Azure VMs
- Spot/preemptible instances for cost savings

### Team Collaboration

- Shared configurations
- Shared disk images
- Access control
- Audit logging

### Phase 7 Deliverables

- [ ] Remote worker system
- [ ] Multi-host execution
- [ ] ARM64 support
- [ ] Bare-metal integration
- [ ] Cloud runners
- [ ] Team collaboration features

---

## Technology References

### QEMU

- QEMU documentation: https://www.qemu.org/docs/master/
- qemu-img: Disk image management
- qemu-system-*: System emulation
- QMP: QEMU Machine Protocol for control

### libvirt

- libvirt documentation: https://libvirt.org/docs.html
- virsh: Command-line management
- XML domain definitions
- Storage pools and volumes
- Snapshot management

### Virtualization Concepts

- **virtio:** Paravirtualized I/O drivers for performance
- **qcow2:** QEMU Copy-On-Write format for disk images
- **overlay:** Disposable disk layers over base images
- **cloud-init:** Instance initialization for VMs
- **serial console:** Text I/O via emulated serial port
- **SSH:** Secure shell for VM communication

### Kernel Testing

- **KUnit:** In-kernel unit testing framework
- **kselftest:** Kernel self-test suite
- **LTP:** Linux Test Project
- **KGDB:** Kernel GNU Debugger
- **GDB:** GNU Debugger (for userspace and QEMU)

### Debugging

- **GDB + QEMU:** Remote debugging of kernel
- **KGDB:** In-kernel debugger via serial
- **ftrace:** Function tracing
- **perf:** Performance analysis
- **crash:** Kernel crash dump analysis
