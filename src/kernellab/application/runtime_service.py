from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kernellab.application.job_service import JobService  # noqa: TC001
from kernellab.config.loader import KernellabConfig  # noqa: TC001
from kernellab.domain.enums import JobType
from kernellab.exceptions import ProviderNotFoundError, RuntimeExecutionError
from kernellab.logging import get_logger
from kernellab.providers.registry import ProviderRegistry  # noqa: TC001

if TYPE_CHECKING:
    from kernellab.domain.job import Job
    from kernellab.providers.base import Provider, ProviderResult

logger = get_logger(__name__)


class RuntimeService:
    def __init__(self, job_service: JobService, registry: ProviderRegistry) -> None:
        self._job_service = job_service
        self._registry = registry

    def _get_provider(self, provider_name: str) -> Provider:
        try:
            return self._registry.get(provider_name)
        except KeyError as exc:
            raise ProviderNotFoundError(provider_name) from exc

    def _build_config(self, lab_config: KernellabConfig, lab_id: str = "") -> dict[str, Any]:
        return {
            "lab_id": lab_id,
            "name": lab_config.name,
            "machine": lab_config.machine.model_dump(),
            "kernel": lab_config.kernel.model_dump(),
            "workspace": lab_config.workspace.model_dump(),
            "provider_options": lab_config.provider_options,
        }

    def _check_result(self, result: ProviderResult, job_id: str, operation: str) -> None:
        if not result.success:
            self._job_service.mark_failed(job_id, result.message)
            raise RuntimeExecutionError(f"Provider {operation} failed", result.message)

    def run_lab(self, lab_config: KernellabConfig, lab_id: str) -> tuple[Job, str]:
        job = self._job_service.create_job(lab_id, JobType.RUN)
        self._job_service.mark_running(job.id)

        provider = self._get_provider(lab_config.provider)
        config = self._build_config(lab_config, lab_id)

        result = provider.create(config)
        self._check_result(result, job.id, "create")

        result = provider.start(config)
        self._check_result(result, job.id, "start")

        all_logs: list[str] = []
        for test in lab_config.tests:
            result = provider.execute(config, test.command)
            all_logs.extend(result.logs)
            if not result.success:
                self._job_service.mark_failed(job.id, result.message)
                provider.destroy(config)
                raise RuntimeExecutionError(f"Test '{test.name}' failed", result.message)

        provider.destroy(config)

        combined = "\n".join(all_logs)
        job = self._job_service.mark_success(job.id, logs=combined)
        logger.info("Lab %s executed successfully (job=%s)", lab_id, job.id)
        return job, combined

    def up_lab(self, lab_config: KernellabConfig, lab_id: str) -> tuple[Job, str]:
        """Create + start if not exists, just start if stopped."""
        provider = self._get_provider(lab_config.provider)
        config = self._build_config(lab_config, lab_id)

        status_result = provider.status(config)
        if status_result.success and status_result.data.get("state") in ("running", "starting"):
            job = self._job_service.create_job(lab_id, JobType.START)
            self._job_service.mark_running(job.id)
            combined = "\n".join(status_result.logs)
            job = self._job_service.mark_success(job.id, logs=combined)
            logger.info("Lab %s already running (job=%s)", lab_id, job.id)
            return job, combined

        job = self._job_service.create_job(lab_id, JobType.CREATE)
        self._job_service.mark_running(job.id)

        create_result = provider.create(config)
        if not create_result.success:
            status_result = provider.status(config)
            if status_result.success and status_result.data.get("state") == "stopped":
                self._job_service.mark_running(job.id)
                result = provider.start(config)
                self._check_result(result, job.id, "start")
                combined = "\n".join(result.logs)
                job = self._job_service.mark_success(job.id, logs=combined)
                logger.info("Lab %s started existing VM (job=%s)", lab_id, job.id)
                return job, combined
            self._job_service.mark_failed(job.id, create_result.message)
            raise RuntimeExecutionError("Provider create failed", create_result.message)

        result = provider.start(config)
        self._check_result(result, job.id, "start")

        combined = "\n".join(create_result.logs + result.logs)
        job = self._job_service.mark_success(job.id, logs=combined)
        logger.info("Lab %s brought up successfully (job=%s)", lab_id, job.id)
        return job, combined

    def start_lab(self, lab_config: KernellabConfig, lab_id: str) -> tuple[Job, str]:
        """Start an existing VM."""
        job = self._job_service.create_job(lab_id, JobType.START)
        self._job_service.mark_running(job.id)

        provider = self._get_provider(lab_config.provider)
        config = self._build_config(lab_config, lab_id)

        result = provider.start(config)
        self._check_result(result, job.id, "start")

        combined = "\n".join(result.logs)
        job = self._job_service.mark_success(job.id, logs=combined)
        logger.info("Lab %s started (job=%s)", lab_id, job.id)
        return job, combined

    def stop_lab(
        self, lab_config: KernellabConfig, lab_id: str, force: bool = False
    ) -> tuple[Job, str]:
        """Stop a VM."""
        job = self._job_service.create_job(lab_id, JobType.STOP)
        self._job_service.mark_running(job.id)

        provider = self._get_provider(lab_config.provider)
        config = self._build_config(lab_config, lab_id)

        if force:
            config["force"] = True

        result = provider.stop(config)
        self._check_result(result, job.id, "stop")

        combined = "\n".join(result.logs)
        job = self._job_service.mark_success(job.id, logs=combined)
        logger.info("Lab %s stopped (job=%s)", lab_id, job.id)
        return job, combined

    def destroy_lab(self, lab_config: KernellabConfig, lab_id: str) -> tuple[Job, str]:
        """Destroy a VM."""
        job = self._job_service.create_job(lab_id, JobType.DESTROY)
        self._job_service.mark_running(job.id)

        provider = self._get_provider(lab_config.provider)
        config = self._build_config(lab_config, lab_id)

        result = provider.destroy(config)
        self._check_result(result, job.id, "destroy")

        combined = "\n".join(result.logs)
        job = self._job_service.mark_success(job.id, logs=combined)
        logger.info("Lab %s destroyed (job=%s)", lab_id, job.id)
        return job, combined

    def status_lab(self, lab_config: KernellabConfig, lab_id: str) -> dict[str, Any]:
        """Get VM status from provider."""
        provider = self._get_provider(lab_config.provider)
        config = self._build_config(lab_config, lab_id)

        result = provider.status(config)
        if not result.success:
            raise RuntimeExecutionError("Provider status failed", result.message)

        return {
            "lab_id": lab_id,
            "state": result.data.get("state", "unknown"),
            "data": result.data,
            "logs": result.logs,
        }

    def console_lab(self, lab_config: KernellabConfig, lab_id: str) -> str:
        """Get serial log content."""
        from kernellab.runtime.paths import RuntimePaths

        paths = RuntimePaths()
        log_path = paths.serial_log(lab_id)

        if not log_path.exists():
            logger.warning("Serial log not found for lab %s", lab_id)
            return ""

        try:
            content = log_path.read_text()
            logger.info("Read serial log for lab %s (%d bytes)", lab_id, len(content))
            return content
        except OSError as exc:
            logger.error("Failed to read serial log for lab %s: %s", lab_id, exc)
            raise RuntimeExecutionError("Failed to read serial log", str(exc)) from exc
