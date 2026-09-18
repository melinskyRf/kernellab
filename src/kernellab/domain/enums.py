"""Enumerations for Kernel Lab domain."""

from enum import StrEnum


class LabStatus(StrEnum):
    """Status of a Lab environment."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class JobStatus(StrEnum):
    """Status of a Job execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(StrEnum):
    """Type of job operation."""

    CREATE = "CREATE"
    START = "START"
    STOP = "STOP"
    BUILD = "BUILD"
    TEST = "TEST"
    SNAPSHOT = "SNAPSHOT"
    RESTORE = "RESTORE"
    DESTROY = "DESTROY"
    RUN = "RUN"


class Architecture(StrEnum):
    """Supported machine architectures."""

    X86_64 = "x86_64"
    ARM64 = "arm64"


class ProviderType(StrEnum):
    """Available virtualization providers."""

    FAKE = "fake"
    QEMU = "qemu"
    VIRTUALBOX = "virtualbox"
    LIBVIRT = "libvirt"
    REMOTE = "remote"


class MachineState(StrEnum):
    """State of a virtual machine."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ImageFormat(StrEnum):
    """Virtual machine image formats."""

    OVA = "ova"
    OVF = "ovf"
    VDI = "vdi"
    VMDK = "vmdk"
    QCOW2 = "qcow2"
    RAW = "raw"
