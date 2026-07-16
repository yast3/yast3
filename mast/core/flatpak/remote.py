"""Flatpak remote management core logic."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal


@dataclass
class FlatpakRemote:
    """Represents a Flatpak remote repository."""

    name: str
    url: str
    scope: Literal["system", "user"] = "system"


def list_flatpak_remotes() -> list[FlatpakRemote]:
    """List available Flatpak remotes."""
    if not _is_flatpak_installed():
        return []

    result = _run_command(["flatpak", "remotes", "--columns=name,url,options"])

    remotes: list[FlatpakRemote] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        name = parts[0].strip()
        url = parts[1].strip()
        options = parts[2].lower() if len(parts) > 2 else ""
        scope: Literal["system", "user"] = "user" if "user" in options else "system"

        remotes.append(FlatpakRemote(name=name, url=url, scope=scope))

    return remotes


def add_flatpak_remote(name: str, url: str, scope: Literal["system", "user"] = "system") -> None:
    """Add a Flatpak remote."""
    _validate_remote_args(name, url)
    args = ["flatpak", "remote-add", "--if-not-exists", f"--{scope}", name, url]
    _run_command(args, use_pkexec=scope == "system")


def modify_flatpak_remote_url(name: str, url: str, scope: Literal["system", "user"] = "system") -> None:
    """Modify the URL of an existing Flatpak remote."""
    _validate_remote_args(name, url)
    args = ["flatpak", "remote-modify", f"--{scope}", f"--url={url}", name]
    _run_command(args, use_pkexec=scope == "system")


def delete_flatpak_remote(name: str, scope: Literal["system", "user"] = "system") -> None:
    """Delete an existing Flatpak remote."""
    remote_name = name.strip()
    if not remote_name:
        raise ValueError("Remote name is required.")

    args = ["flatpak", "remote-delete", f"--{scope}", remote_name]
    _run_command(args, use_pkexec=scope == "system")


def _validate_remote_args(name: str, url: str) -> None:
    if not name.strip():
        raise ValueError("Remote name is required.")
    if not url.strip():
        raise ValueError("Remote URL is required.")


def _is_flatpak_installed() -> bool:
    return shutil.which("flatpak") is not None


def _run_command(args: list[str], use_pkexec: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["pkexec", *args] if use_pkexec else args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(error)
    return result
