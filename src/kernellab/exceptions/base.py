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
