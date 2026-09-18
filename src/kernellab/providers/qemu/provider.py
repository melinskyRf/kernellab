from __future__ import annotations

import contextlib
import json
import logging
import socket
import time
from typing import Any, cast

from kernellab.providers.base import Provider, ProviderCapabilities, ProviderInfo, ProviderResult
from kernellab.providers.qemu import commands as qemu
from kernellab.providers.qemu.discovery import detect
from kernellab.providers.qemu.parser import parse_qemu_version
from kernellab.runtime.command_runner import CommandResult, CommandRunner
from kernellab.runtime.exceptions import CommandExecutionError
from kernellab.runtime.paths import RuntimePaths

logger = logging.getLogger(__name__)

_QMP_DEFAULT_PORT = 4444


class QEMUProvider(Provider):
    def __init__(self) -> None:
        self._discovery = detect()
        self._runner = CommandRunner()

    def info(self) -> ProviderInfo:
        return self.probe()

    def probe(self) -> ProviderInfo:
        return ProviderInfo(
            available=self._discovery.available,
            version=parse_qemu_version(self._discovery.version),
            executable=self._discovery.system_executable,
            host_info=self._discovery.acceleration,
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            serial=True,
            snapshots=True,
            guest_exec=False,
        )

    def create(self, config: dict[str, Any]) -> ProviderResult:
        logs: list[str] = []
        lab_id = config.get("lab_id", "unknown")
        cpus = config.get("cpus", 2)
        memory_mb = config.get("memory_mb", 2048)
        disk_size = config.get("disk_size", "20G")
        disk_format = config.get("disk_format", "qcow2")

        try:
            self._ensure_discovered()

            paths = RuntimePaths()
            paths.ensure_lab_dirs(lab_id)

            vm_dir = paths.vm_dir(lab_id)
            disk_path = str(vm_dir / f"disk.{disk_format}")

            cmd = qemu.create_disk(disk_path, format=disk_format, size=disk_size)
            self._run_cmd(self._discovery.img_executable, cmd, logs=logs)
            logs.append(f"Disk created: {disk_path}")

            monitor_port = self._next_monitor_port(lab_id)

            runtime = {
                "lab_id": lab_id,
                "vm_name": f"kernellab-{lab_id}",
                "disk_path": disk_path,
                "disk_format": disk_format,
                "state": "created",
                "cpus": cpus,
                "memory_mb": memory_mb,
                "monitor_port": monitor_port,
            }
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=f"VM for lab '{lab_id}' created",
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

            disk_path = runtime["disk_path"]
            cpus = runtime.get("cpus", 2)
            memory_mb = runtime.get("memory_mb", 2048)
            monitor_port = runtime.get("monitor_port", _QMP_DEFAULT_PORT)

            paths = RuntimePaths()
            serial_log = str(paths.serial_log(lab_id))

            cmd = qemu.start_vm(
                disk_path=disk_path,
                cpus=cpus,
                memory_mb=memory_mb,
                serial_log=serial_log,
                monitor_port=monitor_port,
                acceleration=self._discovery.acceleration,
            )
            serial_path = paths.serial_log(lab_id)
            self._runner.run_background(
                self._discovery.system_executable,
                cmd,
                stdout=serial_path,
                stderr=serial_path,
            )
            logs.append(f"VM started (monitor port: {monitor_port})")

            runtime["state"] = "running"
            runtime["serial_log"] = serial_log
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message="VM started",
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
            monitor_port = runtime.get("monitor_port", _QMP_DEFAULT_PORT)

            if force:
                self._qmp_send(monitor_port, "quit", logs=logs)
                logs.append("VM forced stop via QMP")
            else:
                try:
                    self._qmp_send(monitor_port, "system_powerdown", logs=logs)
                    logs.append("VM ACPI shutdown via QMP")
                    time.sleep(2)
                    resp = self._qmp_query(monitor_port, logs=logs)
                    if resp.get("running", False):
                        self._qmp_send(monitor_port, "quit", logs=logs)
                        logs.append("VM force quit (ACPI shutdown ignored)")
                except Exception:
                    with contextlib.suppress(Exception):
                        self._qmp_send(monitor_port, "quit", logs=logs)
                    logs.append("VM force quit (fallback)")

            runtime["state"] = "stopped"
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message="VM stopped",
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

            if runtime.get("state") == "running":
                monitor_port = runtime.get("monitor_port", _QMP_DEFAULT_PORT)
                with contextlib.suppress(Exception):
                    self._qmp_send(monitor_port, "quit", logs=logs)
                logs.append("VM stopped before destroy")

            return ProviderResult(
                success=True,
                message=f"VM for lab '{lab_id}' destroyed",
                data=runtime,
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
            monitor_port = runtime.get("monitor_port", _QMP_DEFAULT_PORT)

            try:
                resp = self._qmp_query(monitor_port, logs=logs)
                status_str = resp.get("status", "unknown")
            except Exception:
                status_str = runtime.get("state", "unknown")

            runtime["state"] = status_str
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=status_str,
                data={"state": status_str, "monitor_port": monitor_port},
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
            disk_path = runtime["disk_path"]

            overlay_name = f"snapshot-{name}.qcow2"
            paths = RuntimePaths()
            overlay_path = str(paths.vm_dir(lab_id) / overlay_name)

            cmd = qemu.create_overlay(disk_path, overlay_path)
            self._run_cmd(self._discovery.img_executable, cmd, logs=logs)
            logs.append(f"Snapshot overlay created: {overlay_path}")

            snapshots = runtime.get("snapshots", [])
            snapshots.append({"name": name, "path": overlay_path})
            runtime["snapshots"] = snapshots
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=f"Snapshot '{name}' created",
                data={"snapshot_name": name, "path": overlay_path},
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

            snapshots = runtime.get("snapshots", [])
            target = next((s for s in snapshots if s["name"] == snapshot_id), None)
            if not target:
                return ProviderResult(
                    success=False,
                    message=f"Snapshot '{snapshot_id}' not found",
                    logs=logs,
                )

            runtime["disk_path"] = target["path"]
            runtime["state"] = "restored"
            self._save_runtime(lab_id, runtime)

            return ProviderResult(
                success=True,
                message=f"Restored snapshot '{snapshot_id}'",
                data={"snapshot_id": snapshot_id, "path": target["path"]},
                logs=logs,
            )
        except CommandExecutionError as exc:
            return ProviderResult(
                success=False,
                message=f"Failed to restore snapshot: {exc}",
                logs=logs,
            )

    def _run_cmd(
        self,
        executable: str,
        args: list[str],
        logs: list[str] | None = None,
        timeout: int = 60,
        check: bool = True,
    ) -> CommandResult:
        if logs is None:
            logs = []
        result = self._runner.run(executable, args, timeout=timeout, check=check)
        if result.stdout.strip():
            logs.append(result.stdout.strip())
        return result

    def _ensure_discovered(self) -> None:
        if not self._discovery.available:
            raise CommandExecutionError(
                "qemu-system-x86_64", exit_code=-1, stderr="QEMU not found"
            )

    def _next_monitor_port(self, lab_id: str) -> int:
        base = _QMP_DEFAULT_PORT
        lab_hash = hash(lab_id) % 1000
        return base + lab_hash

    def _qmp_send(
        self,
        port: int,
        command: str,
        logs: list[str] | None = None,
    ) -> dict[str, Any]:
        if logs is None:
            logs = []

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(("127.0.0.1", port))
            self._qmp_read_all(sock, logs, "greeting")

            negotiate = json.dumps({"execute": "qmp_capabilities"}) + "\n"
            sock.sendall(negotiate.encode())
            self._qmp_read_all(sock, logs, "capabilities")

            qmp_cmd = json.dumps({"execute": command}) + "\n"
            sock.sendall(qmp_cmd.encode())
            raw = self._qmp_read_all(sock, logs, command)

            last_line = raw.strip().split("\n")[-1] if raw.strip() else "{}"
            result = json.loads(last_line)
            return cast("dict[str, Any]", result)
        finally:
            sock.close()

    def _qmp_read_all(self, sock: socket.socket, logs: list[str], label: str) -> str:
        chunks: list[str] = []
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data.decode(errors="replace"))
                if data.endswith(b"\n"):
                    break
            except TimeoutError:
                break
        raw = "".join(chunks)
        if logs and raw.strip():
            logs.append(f"QMP {label}: {raw.strip()}")
        return raw

    def _qmp_query(
        self,
        port: int,
        logs: list[str] | None = None,
    ) -> dict[str, Any]:
        if logs is None:
            logs = []

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(("127.0.0.1", port))
            self._qmp_read_all(sock, logs, "greeting")

            negotiate = json.dumps({"execute": "qmp_capabilities"}) + "\n"
            sock.sendall(negotiate.encode())
            self._qmp_read_all(sock, logs, "capabilities")

            qmp_cmd = json.dumps({"execute": "query-status"}) + "\n"
            sock.sendall(qmp_cmd.encode())
            raw = self._qmp_read_all(sock, logs, "query-status")

            last_line = raw.strip().split("\n")[-1] if raw.strip() else "{}"
            data = json.loads(last_line)
            return cast("dict[str, Any]", data.get("return", {}))
        finally:
            sock.close()

    def _save_runtime(self, lab_id: str, runtime: dict[str, Any]) -> None:
        paths = RuntimePaths()
        runtime_path = paths.runtime_json(lab_id)
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        runtime_path.write_text(json.dumps(runtime, indent=2))

    def _load_runtime(self, lab_id: str) -> dict[str, Any]:
        paths = RuntimePaths()
        runtime_path = paths.runtime_json(lab_id)
        if not runtime_path.exists():
            return {
                "vm_name": f"kernellab-{lab_id}",
                "lab_id": lab_id,
                "state": "unknown",
            }
        return cast("dict[str, Any]", json.loads(runtime_path.read_text()))
