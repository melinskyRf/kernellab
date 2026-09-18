from __future__ import annotations

from typing import Any

from kernellab.providers.base import Provider, ProviderInfo, ProviderResult


class FakeProvider(Provider):
    def info(self) -> ProviderInfo:
        return ProviderInfo(available=True, version="fake", executable="fake", host_info="fake")

    def create(self, config: dict[str, Any]) -> ProviderResult:
        options = config.get("provider_options", {})
        if options.get("fail_on_create"):
            return ProviderResult(success=False, message="Simulated create failure")

        return ProviderResult(
            success=True,
            message="created",
            logs=["creating environment..."],
            data={"environment_id": "fake-env-001"},
        )

    def start(self, config: dict[str, Any]) -> ProviderResult:
        options = config.get("provider_options", {})
        if options.get("fail_on_start"):
            return ProviderResult(success=False, message="Simulated start failure")

        return ProviderResult(
            success=True,
            message="started",
            logs=["machine started", "kernel boot simulated"],
            data={"machine_id": "fake-machine-001"},
        )

    def stop(self, config: dict[str, Any], force: bool = False) -> ProviderResult:
        return ProviderResult(
            success=True,
            message="stopped",
            logs=["machine stopped"],
        )

    def destroy(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult(
            success=True,
            message="destroyed",
            logs=["environment destroyed"],
        )

    def status(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult(
            success=True,
            message="running",
            data={"state": "running"},
        )

    def execute(self, config: dict[str, Any], command: str) -> ProviderResult:
        options = config.get("provider_options", {})
        logs: list[str] = ["executing tests..."]

        if options.get("fail_on_run"):
            return ProviderResult(
                success=False,
                message="Simulated failure",
                logs=logs,
            )

        logs.append("test completed")
        logs.append("logs collected")

        return ProviderResult(
            success=True,
            message="completed",
            logs=logs,
            data={"command": command, "exit_code": 0},
        )

    def snapshot(self, config: dict[str, Any], name: str) -> ProviderResult:
        return ProviderResult(
            success=True,
            message="snapshot created",
            data={"snapshot_id": f"fake-snap-{name}"},
            logs=[f"snapshot '{name}' created"],
        )

    def restore(self, config: dict[str, Any], snapshot_id: str) -> ProviderResult:
        return ProviderResult(
            success=True,
            message="restored",
            data={"snapshot_id": snapshot_id},
            logs=[f"restored from snapshot '{snapshot_id}'"],
        )
