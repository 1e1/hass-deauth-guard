"""List candidate network interface names (Linux: /sys/class/net)."""

from __future__ import annotations

import os


def get_candidate_interfaces() -> list[str]:
    """Return non-loopback interface names, sorted. Empty if unavailable (e.g. non-Linux)."""
    base = "/sys/class/net"
    if not os.path.isdir(base):
        return []
    out: list[str] = []
    for name in os.listdir(base):
        if name == "lo":
            continue
        if name.startswith(("docker", "veth", "br-", "virbr")):
            continue
        if os.path.isdir(os.path.join(base, name)):
            out.append(name)
    return sorted(out)
