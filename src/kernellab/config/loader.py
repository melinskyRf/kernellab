from pathlib import Path

import yaml
from pydantic import BaseModel, model_validator


class TestConfig(BaseModel):
    name: str
    command: str


class KernelConfig(BaseModel):
    version: str
    image: str | None = None
    source: str | None = None
    config: str | None = None
    cmdline: str | None = None


class MachineConfig(BaseModel):
    architecture: str = "x86_64"
    cpus: int = 2
    memory: str = "2G"
    disk: str = "10G"

    @model_validator(mode="after")
    def validate_cpus(self) -> "MachineConfig":
        if self.cpus <= 0:
            raise ValueError("cpus must be greater than 0")
        return self


class WorkspaceConfig(BaseModel):
    source: str = "."


class KernellabConfig(BaseModel):
    version: int = 1
    name: str
    description: str | None = None
    provider: str = "fake"
    machine: MachineConfig = MachineConfig()
    kernel: KernelConfig = KernelConfig(version="6.12")
    workspace: WorkspaceConfig = WorkspaceConfig()
    tests: list[TestConfig] = []
    provider_options: dict[str, str] = {}

    @model_validator(mode="after")
    def validate_version(self) -> "KernellabConfig":
        if self.version != 1:
            raise ValueError(f"Unsupported config version: {self.version}")
        return self


def load_config(path: str = "kernellab.yaml") -> KernellabConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    return KernellabConfig(**data)


def validate_config(config: KernellabConfig) -> list[str]:
    errors = []

    if not config.name:
        errors.append("name is required")

    if config.version != 1:
        errors.append(f"Unsupported config version: {config.version}")

    if config.machine.cpus <= 0:
        errors.append("machine.cpus must be greater than 0")

    try:
        KernelConfig(**config.kernel.model_dump())
    except Exception as e:
        errors.append(f"kernel config error: {e}")

    for i, test in enumerate(config.tests):
        if not test.name:
            errors.append(f"tests[{i}].name is required")
        if not test.command:
            errors.append(f"tests[{i}].command is required")

    return errors
