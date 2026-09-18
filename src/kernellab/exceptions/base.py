class KernelLabError(Exception):
    def __init__(self, message: str = "An error occurred in Kernel Lab"):
        super().__init__(message)
        self.message = message


class ConfigurationError(KernelLabError):
    def __init__(self, message: str = "Invalid configuration"):
        super().__init__(message)


class LabNotFoundError(KernelLabError):
    def __init__(self, lab_id: str):
        super().__init__(f"Lab '{lab_id}' not found")
        self.lab_id = lab_id


class JobNotFoundError(KernelLabError):
    def __init__(self, job_id: str):
        super().__init__(f"Job '{job_id}' not found")
        self.job_id = job_id


class ProviderError(KernelLabError):
    def __init__(self, provider: str, message: str = "Provider error"):
        self.provider = provider
        super().__init__(f"Provider '{provider}': {message}")


class ProviderNotFoundError(KernelLabError):
    def __init__(self, provider: str):
        super().__init__(f"Provider '{provider}' not found")
        self.provider = provider


class RuntimeExecutionError(KernelLabError):
    def __init__(self, message: str = "Runtime execution failed", details: str = ""):
        self.details = details
        full = f"{message}: {details}" if details else message
        super().__init__(full)


class LabAlreadyExistsError(KernelLabError):
    def __init__(self, lab_id: str):
        super().__init__(f"Lab '{lab_id}' already exists")
        self.lab_id = lab_id


class InvalidConfigError(KernelLabError):
    def __init__(self, message: str = "kernellab.yaml validation failed", path: str = ""):
        self.path = path
        full = f"{message}: {path}" if path else message
        super().__init__(full)


class ImageNotFoundError(KernelLabError):
    def __init__(self, image_id: str):
        super().__init__(f"Image '{image_id}' not found")
        self.image_id = image_id


class ImageAlreadyExistsError(KernelLabError):
    def __init__(self, name: str):
        super().__init__(f"Image '{name}' already exists")
        self.name = name


class HypervisorNotFoundError(KernelLabError):
    def __init__(self, hypervisor: str = "VirtualBox"):
        super().__init__(f"Hypervisor '{hypervisor}' is not available on this system")
        self.hypervisor = hypervisor


class ProviderUnavailableError(KernelLabError):
    def __init__(self, provider: str, reason: str = ""):
        self.provider = provider
        msg = f"Provider '{provider}' is unavailable"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class MachineAlreadyExistsError(KernelLabError):
    def __init__(self, name: str):
        super().__init__(f"Machine '{name}' already exists")
        self.name = name


class MachineNotFoundError(KernelLabError):
    def __init__(self, identifier: str):
        super().__init__(f"Machine '{identifier}' not found")
        self.identifier = identifier


class MachineStartError(KernelLabError):
    def __init__(self, name: str, reason: str = ""):
        self.name = name
        msg = f"Failed to start machine '{name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class MachineStopError(KernelLabError):
    def __init__(self, name: str, reason: str = ""):
        self.name = name
        msg = f"Failed to stop machine '{name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class MachineDestroyError(KernelLabError):
    def __init__(self, name: str, reason: str = ""):
        self.name = name
        msg = f"Failed to destroy machine '{name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class InvalidImageError(KernelLabError):
    def __init__(self, path: str, reason: str = ""):
        self.path = path
        msg = f"Invalid image: '{path}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
