"""Hostname management logic."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

HOSTNAME_FILE = "/etc/hostname"
HOSTS_FILE = "/etc/hosts"


@dataclass
class HostnameInfo:
    """Represents hostname information."""

    current_hostname: str
    hosts_entries: list[str]


def get_current_hostname() -> str:
    """Get the current system hostname.

    Returns:
        The current hostname.

    Raises:
        FileNotFoundError: If /etc/hostname does not exist.
        PermissionError: If cannot read the file.
    """
    with open(HOSTNAME_FILE, "r") as f:
        return f.read().strip()


def load_hosts_file() -> list[str]:
    """Load hosts file as list of lines.

    Returns:
        List of lines from /etc/hosts file.

    Raises:
        FileNotFoundError: If /etc/hosts does not exist.
        PermissionError: If cannot read the file.
    """
    with open(HOSTS_FILE, "r") as f:
        return f.readlines()


def find_localhost_lines(lines: list[str]) -> tuple[int | None, int | None]:
    """Find the line numbers for 127.0.0.1 and ::1 localhost entries.

    Args:
        lines: List of lines from /etc/hosts.

    Returns:
        Tuple of (ipv4_line_index, ipv6_line_index). None if not found.
    """
    ipv4_line = None
    ipv6_line = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split()
        if not parts:
            continue

        ip = parts[0]
        # Check if this line contains localhost
        if "localhost" in parts:
            if ip == "127.0.0.1":
                ipv4_line = i
            elif ip == "::1":
                ipv6_line = i

    return ipv4_line, ipv6_line


def update_hosts_with_hostname(
    lines: list[str], new_hostname: str, old_hostname: str | None = None
) -> list[str]:
    """Update hosts file lines with new hostname.

    The hostname is added after localhost in the 127.0.0.1 and ::1 lines.
    If old_hostname is provided, it will be removed from all lines first.

    Args:
        lines: List of lines from /etc/hosts.
        new_hostname: The new hostname to add.
        old_hostname: The old hostname to remove (if any).

    Returns:
        Updated list of lines.
    """
    updated_lines = lines.copy()

    # Remove old hostname from all lines if provided
    if old_hostname:
        for i, line in enumerate(updated_lines):
            # Remove old hostname from the line
            parts = line.strip().split()
            if len(parts) > 1 and old_hostname in parts[1:]:
                # Keep the IP and other hostnames, remove old_hostname
                new_parts = [parts[0]] + [h for h in parts[1:] if h != old_hostname]
                updated_lines[i] = " ".join(new_parts) + (
                    "\n" if line.endswith("\n") else ""
                )

    # Find and update localhost lines
    ipv4_line, ipv6_line = find_localhost_lines(updated_lines)

    # Update 127.0.0.1 line
    if ipv4_line is not None:
        line = updated_lines[ipv4_line]
        parts = line.strip().split()
        if len(parts) > 1:
            # Check if hostname already exists
            if new_hostname not in parts[1:]:
                # Add hostname after localhost
                localhost_idx = parts.index("localhost")
                parts.insert(localhost_idx + 1, new_hostname)
                updated_lines[ipv4_line] = " ".join(parts) + (
                    "\n" if line.endswith("\n") else ""
                )

    # Update ::1 line
    if ipv6_line is not None:
        line = updated_lines[ipv6_line]
        parts = line.strip().split()
        if len(parts) > 1:
            # Check if hostname already exists
            if new_hostname not in parts[1:]:
                # Add hostname after localhost
                localhost_idx = parts.index("localhost")
                parts.insert(localhost_idx + 1, new_hostname)
                updated_lines[ipv6_line] = " ".join(parts) + (
                    "\n" if line.endswith("\n") else ""
                )

    return updated_lines


def set_hostname(
    new_hostname: str, use_pkexec: bool = True
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Set the hostname and update /etc/hosts file.

    Args:
        new_hostname: The new hostname to set.
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
        status can be "ok", "permission_denied", "pkexec_failed", or "error".
    """
    script_path = Path(__file__).parent / "set_hostname.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path), new_hostname],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "Hostname updated successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to set hostname")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path), new_hostname],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "Hostname updated successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to set hostname")
