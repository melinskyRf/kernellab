from __future__ import annotations

import json
import re


def parse_qemu_version(raw: str) -> str:
    match = re.search(r"QEMU emulator version\s+([\d.]+)", raw)
    if match:
        return match.group(1)
    return raw.strip()


def parse_qmp_response(raw: str) -> dict:
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return {}
