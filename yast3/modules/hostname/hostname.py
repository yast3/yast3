"""Hostname management logic."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
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


def update_hosts_with_hostname(lines: list[str], new_hostname: str, old_hostname: str | None = None) -> list[str]:
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
                # Preserve original line formatting (tabs/spaces)
                stripped = line.strip()
                if '\t' in line:
                    sep = '\t'
                else:
                    sep = ' '
                updated_lines[i] = sep.join(new_parts) + '\n' if line.endswith('\n') else sep.join(new_parts)
    
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
                # Preserve original line formatting
                if '\t' in line:
                    sep = '\t'
                else:
                    sep = ' '
                updated_lines[ipv4_line] = sep.join(parts) + '\n' if line.endswith('\n') else sep.join(parts)
    
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
                # Preserve original line formatting
                if '\t' in line:
                    sep = '\t'
                else:
                    sep = ' '
                updated_lines[ipv6_line] = sep.join(parts) + '\n' if line.endswith('\n') else sep.join(parts)
    
    return updated_lines


def save_hostname_file(hostname: str, use_pkexec: bool = True) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Save hostname to /etc/hostname file.
    
    Args:
        hostname: The hostname to save.
        use_pkexec: If True, use pkexec for privilege escalation on permission error.
    
    Returns:
        "ok" on success,
        "permission_denied" if direct write fails and use_pkexec is False,
        "pkexec_failed" if pkexec authentication fails,
        "error" for other errors.
    """
    content = hostname + "\n"
    
    # Try direct write first
    try:
        with open(HOSTNAME_FILE, "w") as f:
            f.write(content)
        return "ok"
    except PermissionError:
        if not use_pkexec:
            return "permission_denied"
    except Exception:
        return "error"
    
    # Use pkexec to get root permission
    try:
        # Write to a temporary file first
        with tempfile.NamedTemporaryFile(mode="w", suffix=".hostname", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Use pkexec to copy the file to /etc/hostname
        result = subprocess.run(
            ["pkexec", "cp", tmp_path, HOSTNAME_FILE],
            capture_output=True,
            text=True,
        )
        
        # Clean up temp file
        subprocess.run(["rm", "-f", tmp_path], capture_output=True)
        
        if result.returncode == 0:
            return "ok"
        else:
            return "pkexec_failed"
    except Exception:
        return "error"


def save_hosts_file(lines: list[str], use_pkexec: bool = True) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Save hosts file lines to /etc/hosts file.
    
    Args:
        lines: List of lines to save.
        use_pkexec: If True, use pkexec for privilege escalation on permission error.
    
    Returns:
        "ok" on success,
        "permission_denied" if direct write fails and use_pkexec is False,
        "pkexec_failed" if pkexec authentication fails,
        "error" for other errors.
    """
    content = "".join(lines)
    
    # Try direct write first
    try:
        with open(HOSTS_FILE, "w") as f:
            f.write(content)
        return "ok"
    except PermissionError:
        if not use_pkexec:
            return "permission_denied"
    except Exception:
        return "error"
    
    # Use pkexec to get root permission
    try:
        # Write to a temporary file first
        with tempfile.NamedTemporaryFile(mode="w", suffix=".hosts", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Use pkexec to copy the file to /etc/hosts
        result = subprocess.run(
            ["pkexec", "cp", tmp_path, HOSTS_FILE],
            capture_output=True,
            text=True,
        )
        
        # Clean up temp file
        subprocess.run(["rm", "-f", tmp_path], capture_output=True)
        
        if result.returncode == 0:
            return "ok"
        else:
            return "pkexec_failed"
    except Exception:
        return "error"


def set_system_hostname(hostname: str, use_pkexec: bool = True) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Set the system hostname using hostnamectl.
    
    Args:
        hostname: The hostname to set.
        use_pkexec: If True, use pkexec for privilege escalation.
    
    Returns:
        "ok" on success,
        "permission_denied" if command fails and use_pkexec is False,
        "pkexec_failed" if pkexec authentication fails,
        "error" for other errors.
    """
    try:
        result = subprocess.run(
            ["hostnamectl", "set-hostname", hostname],
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            return "ok"
        elif result.returncode == 1 or "Permission denied" in result.stderr:
            if not use_pkexec:
                return "permission_denied"
            
            # Try with pkexec
            result = subprocess.run(
                ["pkexec", "hostnamectl", "set-hostname", hostname],
                capture_output=True,
                text=True,
            )
            
            if result.returncode == 0:
                return "ok"
            else:
                return "pkexec_failed"
        else:
            return "error"
    except Exception:
        return "error"


def set_hostname(new_hostname: str, use_pkexec: bool = True) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Set the hostname and update /etc/hosts file.
    
    Args:
        new_hostname: The new hostname to set.
        use_pkexec: If True, use pkexec for privilege escalation.
    
    Returns:
        Tuple of (status, message).
        status can be "ok", "permission_denied", "pkexec_failed", or "error".
    """
    try:
        # Get current hostname
        current_hostname = get_current_hostname()
        
        # Load hosts file
        hosts_lines = load_hosts_file()
        
        # Update hosts file with new hostname
        updated_hosts_lines = update_hosts_with_hostname(hosts_lines, new_hostname, current_hostname)
        
        # Save hostname file
        hostname_result = save_hostname_file(new_hostname, use_pkexec)
        if hostname_result != "ok":
            return (hostname_result, f"Failed to save {HOSTNAME_FILE}")
        
        # Save hosts file
        hosts_result = save_hosts_file(updated_hosts_lines, use_pkexec)
        if hosts_result != "ok":
            return (hosts_result, f"Failed to save {HOSTS_FILE}")
        
        # Set system hostname
        system_result = set_system_hostname(new_hostname, use_pkexec)
        if system_result != "ok":
            return (system_result, "Failed to set system hostname")
        
        return ("ok", "Hostname updated successfully")
    
    except FileNotFoundError as e:
        return ("error", f"File not found: {e}")
    except PermissionError:
        return ("permission_denied", "Permission denied")
    except Exception as e:
        return ("error", f"Error: {e}")