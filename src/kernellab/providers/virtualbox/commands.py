from __future__ import annotations


def create_vm(name: str, ostype: str = "Linux_64") -> list[str]:
    return ["createvm", "--name", name, "--ostype", ostype, "--register"]


def modify_vm(vm_name: str, cpus: int, memory_mb: int) -> list[str]:
    return [
        "modifyvm",
        vm_name,
        "--cpus",
        str(cpus),
        "--memory",
        str(memory_mb),
        "--vram",
        "16",
        "--ioapic",
        "on",
        "--acpi",
        "on",
        "--ioapic",
        "on",
    ]


def storagectl(
    vm_name: str,
    port: int,
    device: int,
    type: str,
    medium: str,
) -> list[str]:
    return [
        "storageattach",
        vm_name,
        "--storagectl",
        "SATA",
        "--port",
        str(port),
        "--device",
        str(device),
        "--type",
        type,
        "--medium",
        medium,
    ]


def nat_network(vm_name: str, network_name: str) -> list[str]:
    return [
        "modifyvm",
        vm_name,
        "--nic1",
        "natnetwork",
        "--nat-network1",
        network_name,
    ]


def start_vm(vm_name: str, headless: bool = True) -> list[str]:
    type_arg = "headless" if headless else "gui"
    return ["startvm", vm_name, "--type", type_arg]


def control_vm(vm_name: str, action: str) -> list[str]:
    return ["controlvm", vm_name, action]


def show_vm_info(vm_name: str) -> list[str]:
    return ["showvminfo", vm_name, "--machinereadable"]


def list_vms() -> list[str]:
    return ["list", "vms"]


def unregistervm(vm_name: str, delete: bool = False) -> list[str]:
    cmd = ["unregistervm", vm_name]
    if delete:
        cmd.append("--delete")
    return cmd
