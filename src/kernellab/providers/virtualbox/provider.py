from __future__ import annotations

import json
import logging
from typing import Any, cast

from kernellab.providers.base import Provider, ProviderCapabilities, ProviderInfo, ProviderResult
from kernellab.providers.virtualbox import commands as vbox
from kernellab.providers.virtualbox.discovery import detect
from kernellab.providers.virtualbox.parser import parse_vm_info, parse_vm_state
from kernellab.runtime.command_runner import CommandResult, CommandRunner
from kernellab.runtime.exceptions import CommandExecutionError
from kernellab.runtime.paths import RuntimePaths

logger = logging.getLogger(__name__)


class VirtualBoxProvider(Provider):
    def __init__(self) -> None:
        self._discovery = detect()
        self._runner = CommandRunner()

    def info(self) -> ProviderInfo:
        return self.probe()

    def probe(self) -> ProviderInfo:
        return ProviderInfo(
            available=self._discovery.available,
            version=self._discovery.version,
            executable=self._discovery.executable,
            host_info=self._discovery.host_info,
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            serial=False,
            snapshots=True,
            guest_exec=False,
        )

    def create(self, config: dict[str, Any]) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")
        cpus = config.get("cpus", 2)
        memory_mb = config.get("memory_mb", 2048)
        iso_path = config.get("iso_path", "")
        vm_name = config.get("vm_name", f"kernellab-{lab_id}")

        try:
            self._ensure_discovered()

            paths = RuntimePaths()
            paths.ensure_lab_dirs(lab_id)

            cmd = vbox.create_vm(vm_name, ostype="Linux_64")
            self._run(cmd, logs=logs)
            logs.append(f"VM '{vm_name}' created")

            cmd = vbox.modify_vm(vm_name, cpus=cpus, memory_mb=memory_mb)
            self._run(cmd, logs=logs)
            logs.append(f"VM '{vm_name}' modified: cpus={cpus}, memory={memory_mb}MB")

            if iso_path:
                cmd = vbox.storagectl(
                    vm_name,
                    port=0,
                    device=0,
                    type="dvddrive",
                    medium=iso_path,
                )
                self._run(cmd, logs=logs)
                logs.append(f"Storage attached: {iso_path}")

            cmd = vbox.nat_network(vm_name, "KernLabNAT")
            self._run(cmd, logs=logs)
            logs.append("Network configured")

            runtime = {
                "vm_name": vm_name,
                "lab_id": lab_id,
                "state": "created",
                "cpus": cpus,
                "memory_mb": memory_mb,
            }
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=f"VM '{vm_name}' created successfully",
                data=runtime,
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to create VM: {exc}",
                logs=logs,
            )

    def start(self, config: dict[str, Any]) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")

        try:
            self._ensure_discovered()
            runtime = self._load_runtime(lab_id)
            vm_name = runtime["vm_name"]

            cmd = vbox.start_vm(vm_name, headless=True)
            self._run(cmd, logs=logs)
            logs.append(f"VM '{vm_name}' started")

            runtime["state"] = "running"
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=f"VM '{vm_name}' started",
                data=runtime,
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to start VM: {exc}",
                logs=logs,
            )

    def stop(self, config: dict[str, Any], force: bool = False) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")

        try:
            self._ensure_discovered()
            runtime = self._load_runtime(lab_id)
            vm_name = runtime["vm_name"]

            if force:
                cmd = vbox.control_vm(vm_name, "poweroff")
                self._run(cmd, logs=logs, check=False)
                logs.append(f"VM '{vm_name}' poweroff (forced)")
            else:
                try:
                    cmd = vbox.control_vm(vm_name, "acpipowerbutton")
                    self._run(cmd, logs=logs, timeout=30, check=False)
                    logs.append(f"VM '{vm_name}' ACPI shutdown requested")
                except CommandExecutionError:
                    cmd = vbox.control_vm(vm_name, "poweroff")
                    self._run(cmd, logs=logs, check=False)
                    logs.append(f"VM '{vm_name}' poweroff (fallback)")

            runtime["state"] = "stopped"
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=f"VM '{vm_name}' stopped",
                data=runtime,
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to stop VM: {exc}",
                logs=logs,
            )

    def destroy(self, config: dict[str, Any]) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")

        try:
            self._ensure_discovered()
            runtime = self._load_runtime(lab_id)
            vm_name = runtime["vm_name"]

            status_cmd = vbox.show_vm_info(vm_name)
            result = self._run(status_cmd, logs=logs, check=False)
            info = parse_vm_info(result.stdout)
            state = parse_vm_state(info)

            if state == "RUNNING":
                cmd = vbox.control_vm(vm_name, "poweroff")
                self._run(cmd, logs=logs, check=False)
                logs.append(f"VM '{vm_name}' stopped before destroy")

            cmd = vbox.unregistervm(vm_name, delete=True)
            self._run(cmd, logs=logs)
            logs.append(f"VM '{vm_name}' unregistered and deleted")

            return ProviderResult(
                success=True,
                message=f"VM '{vm_name}' destroyed",
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to destroy VM: {exc}",
                logs=logs,
            )

    def status(self, config: dict[str, Any]) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")

        try:
            self._ensure_discovered()
            runtime = self._load_runtime(lab_id)
            vm_name = runtime["vm_name"]

            cmd = vbox.show_vm_info(vm_name)
            result = self._run(cmd, logs=logs, check=False)
            info = parse_vm_info(result.stdout)
            state = parse_vm_state(info)

            runtime["state"] = state.lower()
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=state,
                data={"status": state, "vm_name": vm_name},
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to get status: {exc}",
                logs=logs,
            )

    def execute(self, config: dict[str, Any], command: str) -> ProviderResult:
        return ProviderResult(
            success=False,
            message="Guest execution not yet implemented (Phase 3)",
            data={"command": command},
        )

    def snapshot(self, config: dict[str, Any], name: str) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")

        try:
            self._ensure_discovered()
            runtime = self._load_runtime(lab_id)
            vm_name = runtime["vm_name"]

            cmd = vbox.control_vm(vm_name, f"snapshot {name}")
            self._run(cmd, logs=logs)
            logs.append(f"Snapshot '{name}' created for VM '{vm_name}'")

            return ProviderResult(
                success=True,
                message=f"Snapshot '{name}' created",
                data={"vm_name": vm_name, "snapshot_name": name},
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to create snapshot: {exc}",
                logs=logs,
            )

    def restore(self, config: dict[str, Any], snapshot_id: str) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")

        try:
            self._ensure_discovered()
            runtime = self._load_runtime(lab_id)
            vm_name = runtime["vm_name"]

            cmd = vbox.control_vm(vm_name, f"restoreSnapshot {snapshot_id}")
            self._run(cmd, logs=logs)
            logs.append(f"Restored snapshot '{snapshot_id}' for VM '{vm_name}'")

            return ProviderResult(
                success=True,
                message=f"Restored snapshot '{snapshot_id}'",
                data={"vm_name": vm_name, "snapshot_id": snapshot_id},
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to restore snapshot: {exc}",
                logs=logs,
            )

    def _run(
        self,
        args: list[str],
        logs: list[str] | None = None,
        timeout: int = 60,
        check: bool = True,
    ) -> CommandResult:
        if logs is None:
            logs = []
        result = self._runner.run(
            self._discovery.executable,
            args,
            timeout=timeout,
            check=check,
        )
        if result.stdout.strip():
            logs.append(result.stdout.strip())
        return result

    def _ensure_discovered(self) -> None:
        if not self._discovery.available:
            raise CommandExecutionError(
                "VBoxManage", exit_code=-1, stderr="VirtualBox not found"
            )

    def _save_runtime(self, lab_id: str, runtime: dict[str, Any]) -> None:
        paths = RuntimePaths()
        runtime_path = paths.runtime_json(lab_id)
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        runtime_path.write_text(json.dumps(runtime, indent=2))

    def _load_runtime(self, lab_id: str) -> dict[str, Any]:
        paths = RuntimePaths()
        runtime_path = paths.runtime_json(lab_id)
        if not runtime_path.exists():
            return {"vm_name": f"kernellab-{lab_id}", "lab_id": lab_id, "state": "unknown"}
        return cast("dict[str, Any]", json.loads(runtime_path.read_text()))
