from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./.kernellab/kernellab.db"
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    project_root: str = "."

    model_config = {"env_prefix": "KERNELLAB_", "env_file": ".env"}
