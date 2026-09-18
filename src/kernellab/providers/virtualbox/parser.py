from __future__ import annotations

import re

_STATE_MAP: dict[str, str] = {
    "running": "RUNNING",
    "poweroff": "STOPPED",
    "saved": "STOPPED",
    "aborted": "FAILED",
    "paused": "STOPPED",
    "stuck": "FAILED",
    "gururinging": "RUNNING",
}


def parse_vm_info(raw: str) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^(\w+)="?(.*)"?$', line)
        if match:
            key, value = match.groups()
            info[key] = value.rstrip('"')
    return info


def parse_vm_state(info: dict[str, str]) -> str:
    vbox_state = info.get("VMState", "").lower().strip('"')
    return _STATE_MAP.get(vbox_state, "UNKNOWN")


def parse_vm_list(raw: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    pattern = re.compile(r'^"([^"]+)"\s+\{(.+)\}$')
    for line in raw.splitlines():
        line = line.strip()
        match = pattern.match(line)
        if match:
            name = match.group(1)
            uuid = match.group(2)
            results.append((name, uuid))
    return results
