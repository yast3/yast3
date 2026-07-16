"""Flatpak package management core logic."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal


@dataclass
class FlatpakPackage:
    """Represents an installed Flatpak application."""

    app_id: str
    remote: str
    name: str = ""
    description: str = ""
    version: str = ""
    branch: str = ""
    installed_size: str = ""
    download_size: str = ""
    scope: Literal["system", "user"] = "system"


def list_flatpak_packages() -> list[FlatpakPackage]:
    """List installed Flatpak applications."""
    if not _is_flatpak_installed():
        return []

    result = _run_command(
        [
            "flatpak",
            "list",
            "--app",
            "--columns=application,name,description,version,branch,origin,size,installation",
        ]
    )

    packages: list[FlatpakPackage] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 1:
            continue

        app_id = parts[0].strip()
        name = parts[1].strip() if len(parts) > 1 else ""
        description = parts[2].strip() if len(parts) > 2 else ""
        version = parts[3].strip() if len(parts) > 3 else ""
        branch = parts[4].strip() if len(parts) > 4 else ""
        remote = parts[5].strip() if len(parts) > 5 else ""
        installed_size = parts[6].strip() if len(parts) > 6 else ""
        installation = parts[7].strip().lower() if len(parts) > 7 else "system"
        scope: Literal["system", "user"] = "user" if "user" in installation else "system"

        if app_id:
            packages.append(
                FlatpakPackage(
                    app_id=app_id,
                    remote=remote,
                    name=name,
                    description=description,
                    version=version,
                    branch=branch,
                    installed_size=installed_size,
                    scope=scope,
                )
            )

    return packages


def search_flatpak_packages(query: str, remote: str = "flathub") -> list[str]:
    """Search application IDs from a Flatpak remote."""
    normalized_query = query.strip().lower()
    normalized_remote = remote.strip()
    if not normalized_query:
        raise ValueError("Search query is required.")
    if not normalized_remote:
        raise ValueError("Flatpak remote is required.")
    packages = list_remote_flatpak_packages(normalized_remote)
    return [pkg.app_id for pkg in packages if normalized_query in pkg.app_id.lower()]


def list_remote_flatpak_packages(remote: str = "flathub") -> list[FlatpakPackage]:
    """List all application metadata from a Flatpak remote."""
    normalized_remote = remote.strip()
    if not normalized_remote:
        raise ValueError("Flatpak remote is required.")
    if not _is_flatpak_installed():
        return []

    result = _run_command(
        [
            "flatpak",
            "remote-ls",
            "--app",
            "--columns=application,name,description,version,download-size,branch",
            normalized_remote,
        ]
    )

    packages: list[FlatpakPackage] = []
    seen: set[str] = set()
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")
        app_id = parts[0].strip() if len(parts) > 0 else ""
        if not app_id or app_id in seen:
            continue

        name = parts[1].strip() if len(parts) > 1 else ""
        description = parts[2].strip() if len(parts) > 2 else ""
        version = parts[3].strip() if len(parts) > 3 else ""
        download_size = parts[4].strip() if len(parts) > 4 else ""
        branch = parts[5].strip() if len(parts) > 5 else ""

        seen.add(app_id)
        packages.append(
            FlatpakPackage(
                app_id=app_id,
                remote=normalized_remote,
                name=name,
                description=description,
                version=version,
                branch=branch,
                download_size=download_size,
                scope="system",
            )
        )

    return packages


def install_flatpak_package(
    app_id: str,
    remote: str = "flathub",
    scope: Literal["system", "user"] = "system",
) -> None:
    """Install a Flatpak application from a remote."""
    normalized_app = app_id.strip()
    normalized_remote = remote.strip()
    if not normalized_app:
        raise ValueError("Flatpak app id is required.")
    if not normalized_remote:
        raise ValueError("Flatpak remote is required.")

    args = ["flatpak", "install", "-y", f"--{scope}", normalized_remote, normalized_app]
    _run_command(args, use_pkexec=scope == "system")


def uninstall_flatpak_package(app_id: str, scope: Literal["system", "user"] = "system") -> None:
    """Uninstall a Flatpak application."""
    normalized_app = app_id.strip()
    if not normalized_app:
        raise ValueError("Flatpak app id is required.")

    args = ["flatpak", "uninstall", "-y", f"--{scope}", normalized_app]
    _run_command(args, use_pkexec=scope == "system")


def _run_command(args: list[str], use_pkexec: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["pkexec", *args] if use_pkexec else args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(error)
    return result


def _is_flatpak_installed() -> bool:
    return shutil.which("flatpak") is not None
