from __future__ import annotations


def create_disk(
    image_path: str,
    format: str = "qcow2",
    size: str | None = None,
) -> list[str]:
    cmd = ["create", "-f", format, image_path]
    if size:
        cmd.append(size)
    return cmd


def convert_image(
    input_path: str,
    output_path: str,
    output_format: str,
) -> list[str]:
    return ["convert", "-f", "raw", "-O", output_format, input_path, output_path]


def create_overlay(
    base_path: str,
    overlay_path: str,
    format: str = "qcow2",
) -> list[str]:
    return [
        "create",
        "-f",
        format,
        "-b",
        base_path,
        "-F",
        format,
        overlay_path,
    ]


def start_vm(
    disk_path: str,
    cpus: int = 2,
    memory_mb: int = 2048,
    serial_log: str | None = None,
    monitor_port: int | None = None,
    network_opts: str | None = None,
    acceleration: str = "tcg",
) -> list[str]:
    cmd = [
        "-m",
        str(memory_mb),
        "-smp",
        str(cpus),
        "-drive",
        f"file={disk_path},format=qcow2,if=virtio",
        "-nographic",
        "-serial",
        "mon:stdio",
        "-accel",
        acceleration,
    ]

    if serial_log:
        cmd.extend(["-serial", f"file:{serial_log}"])

    if monitor_port:
        cmd.extend([
            "-qmp",
            f"tcp:127.0.0.1:{monitor_port},server,nowait",
        ])

    if network_opts:
        cmd.extend(["-netdev", network_opts])
    else:
        cmd.extend(["-netdev", "user,id=net0,hostfwd=tcp::8080-:80"])
        cmd.extend(["-device", "virtio-net-pci,netdev=net0"])

    return cmd


def stop_vm(monitor_port: int) -> list[str]:
    return [
        "-qmp",
        f"tcp:127.0.0.1:{monitor_port}",
        "-S",
    ]


def query_status(monitor_port: int) -> list[str]:
    return [
        "-qmp",
        f"tcp:127.0.0.1:{monitor_port}",
    ]
