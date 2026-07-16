"""Compatibility exports for Flatpak core helpers."""

import shutil
import subprocess

def is_flatpak_installed() -> bool:
    """Check whether the flatpak executable is available."""
    return shutil.which("flatpak") is not None


def install_flatpak_pkexec() -> None:
    """Install Flatpak using zypper with root permissions."""
    _run_command(["zypper", "--non-interactive", "install", "-y", "flatpak"], use_pkexec=True)


def remove_flatpak_pkexec() -> None:
    """Remove Flatpak using zypper with root permissions."""
    _run_command(["zypper", "--non-interactive", "remove", "-y", "flatpak"], use_pkexec=True)


def _run_command(args: list[str], use_pkexec: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["pkexec", *args] if use_pkexec else args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(error)
    return result

__all__ = [
    "install_flatpak_pkexec",
    "is_flatpak_installed",
    "remove_flatpak_pkexec",
]
