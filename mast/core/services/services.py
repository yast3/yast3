"""Systemd service listing and command helpers."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class ServiceEntry:
    """Represents a systemd service unit."""

    name: str
    scope: str
    active_state: str
    sub_state: str
    enabled_state: str
    description: str

    @property
    def status_text(self) -> str:
        if self.sub_state and self.sub_state != self.active_state:
            return f"{self.active_state} ({self.sub_state})"
        return self.active_state

    @property
    def enabled_text(self) -> str:
        return self.enabled_state or "unknown"


def _status_rank(active_state: str) -> int:
    order = {
        "active": 0,
        "activating": 1,
        "reloading": 2,
        "failed": 3,
        "inactive": 4,
        "deactivating": 5,
    }
    return order.get(active_state, 6)


def _scope_prefix(scope: str) -> list[str]:
    return ["systemctl", "--user"] if scope == "user" else ["systemctl"]


def _run_systemctl_json(command: list[str]) -> list[dict[str, object]]:
    result = subprocess.run(
        command,
        capture_output=True,
        check=True,
        text=True,
    )
    payload = result.stdout.strip()
    if not payload:
        return []

    data = json.loads(payload)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        rows = data.get("units") or data.get("unit_files") or []
        if isinstance(rows, list):
            return [item for item in rows if isinstance(item, dict)]
    return []


def _load_scope_services(scope: str) -> list[ServiceEntry]:
    unit_command = [
        *_scope_prefix(scope),
        "list-units",
        "--type=service",
        "--all",
        "--plain",
        "--no-legend",
        "--no-pager",
        "--output=json",
    ]
    unit_file_command = [
        *_scope_prefix(scope),
        "list-unit-files",
        "--type=service",
        "--plain",
        "--no-legend",
        "--no-pager",
        "--output=json",
    ]

    units = _run_systemctl_json(unit_command)
    unit_files = _run_systemctl_json(unit_file_command)
    enabled_by_name = {
        str(item.get("unit_file", "")): str(item.get("state", "unknown"))
        for item in unit_files
        if item.get("unit_file")
    }

    services: list[ServiceEntry] = []
    for item in units:
        name = str(item.get("unit", "")).strip()
        if not name.endswith(".service"):
            continue

        services.append(
            ServiceEntry(
                name=name,
                scope=scope,
                active_state=str(item.get("active", "unknown")),
                sub_state=str(item.get("sub", "")),
                enabled_state=enabled_by_name.get(name, "unknown"),
                description=str(item.get("description", "")),
            )
        )

    return services


def list_services() -> list[ServiceEntry]:
    """List system and user services, sorted with active services first."""

    services: list[ServiceEntry] = []
    for scope in ("system", "user"):
        try:
            services.extend(_load_scope_services(scope))
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            continue

    services.sort(
        key=lambda entry: (
            _status_rank(entry.active_state),
            entry.scope,
            entry.name.lower(),
        )
    )
    return services


def build_service_action_command(service: ServiceEntry, action: str) -> list[str]:
    """Build a systemctl command for a service action."""

    if action not in {"start", "stop", "enable", "disable"}:
        raise ValueError(f"Unsupported action: {action}")

    base = _scope_prefix(service.scope) + [action, service.name]
    if service.scope == "system":
        return ["pkexec", *base]
    return base


def build_service_logs_command(service: ServiceEntry, lines: int = 200) -> list[str]:
    """Build a journalctl command for a service."""

    base = ["journalctl"]
    if service.scope == "user":
        base.append("--user")
    base.extend(["-u", service.name, "-n", str(lines), "--no-pager"])
    if service.scope == "system":
        return ["pkexec", *base]
    return base