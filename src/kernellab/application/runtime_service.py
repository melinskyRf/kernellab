from __future__ import annotations

from kernellab.application.job_service import JobService  # noqa: TC001
from kernellab.config.loader import KernellabConfig  # noqa: TC001
from kernellab.domain.enums import JobType
from kernellab.exceptions import ProviderNotFoundError, RuntimeExecutionError
from kernellab.logging import get_logger
from kernellab.providers.registry import ProviderRegistry  # noqa: TC001

logger = get_logger(__name__)


class RuntimeService:
    def __init__(self, job_service: JobService, registry: ProviderRegistry) -> None:
        self._job_service = job_service
        self._registry = registry

    def run_lab(self, lab_config: KernellabConfig, lab_id: str) -> tuple:
        job = self._job_service.create_job(lab_id, JobType.RUN)
        self._job_service.mark_running(job.id)

        provider_name = lab_config.provider
        try:
            provider = self._registry.get(provider_name)
        except KeyError as exc:
            self._job_service.mark_failed(job.id, str(exc))
            raise ProviderNotFoundError(provider_name) from exc

        config = {
            "name": lab_config.name,
            "machine": lab_config.machine.model_dump(),
            "kernel": lab_config.kernel.model_dump(),
            "workspace": lab_config.workspace.model_dump(),
            "provider_options": lab_config.provider_options,
        }

        result = provider.create(config)
        if not result.success:
            self._job_service.mark_failed(job.id, result.message)
            raise RuntimeExecutionError("Provider create failed", result.message)

        result = provider.start(config)
        if not result.success:
            self._job_service.mark_failed(job.id, result.message)
            raise RuntimeExecutionError("Provider start failed", result.message)

        all_logs: list[str] = []
        for test in lab_config.tests:
            result = provider.execute(config, test.command)
            all_logs.extend(result.logs)

        provider.destroy(config)

        combined = "\n".join(all_logs)
        job = self._job_service.mark_success(job.id, logs=combined)
        logger.info("Lab %s executed successfully (job=%s)", lab_id, job.id)
        return job, combined
