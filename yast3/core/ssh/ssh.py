"""SSH config file reading and writing logic."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from typing import Literal

SSH_CONFIG_FILE = os.path.expanduser("~/.ssh/config")
SSH_CONFIG_DIR = os.path.expanduser("~/.ssh")


@dataclass
class SSHConfigEntry:
    """Represents a single SSH config host entry."""

    enabled: bool
    host: str
    options: dict[str, str] = field(default_factory=dict)
    comment: str = ""
    editable: bool = True

    def is_default(self) -> bool:
        """Check if this is the default entry (Host *)."""
        return self.host == "*"

    def has_option(self, key: str) -> bool:
        """Check if the entry has a specific option."""
        return key.lower() in (k.lower() for k in self.options.keys())

    def get_option(self, key: str, default: str = "") -> str:
        """Get an option value, case-insensitive."""
        for k, v in self.options.items():
            if k.lower() == key.lower():
                return v
        return default


def _parse_ssh_config_line(line: str) -> tuple[str, str, str]:
    """Parse a single SSH config line.

    Returns:
        (key, value, comment)
        - key: option key (empty for comments/empty lines)
        - value: option value (empty for comments/empty lines)
        - comment: comment content (including #)
    """
    stripped = line.strip()

    # Empty line
    if not stripped:
        return "", "", ""

    # Comment line
    if stripped.startswith("#"):
        return "", "", stripped

    # Check for inline comment
    comment_pos = stripped.find("#")
    if comment_pos != -1:
        content = stripped[:comment_pos].strip()
        comment = stripped[comment_pos:]
    else:
        content = stripped
        comment = ""

    # Parse key-value pair
    parts = content.split(None, 1)
    if len(parts) >= 2:
        return parts[0], parts[1], comment

    return "", "", line


def load_ssh_config() -> list[SSHConfigEntry]:
    """Load SSH config from ~/.ssh/config file.

    Returns:
        List of SSHConfigEntry objects.

    Raises:
        PermissionError: If cannot read the file.
        FileNotFoundError: If the file does not exist.
    """
    entries: list[SSHConfigEntry] = []

    with open(SSH_CONFIG_FILE, "r") as f:
        lines = f.readlines()

    current_entry: SSHConfigEntry | None = None
    current_comment = ""

    for line in lines:
        line = line.rstrip("\n\r")
        key, value, comment = _parse_ssh_config_line(line)

        # Handle comment lines
        if key == "" and value == "" and comment:
            if current_entry is None:
                # This is a comment before any Host entry
                current_comment += comment + "\n"
            else:
                # Add comment to current entry's comment
                if current_entry.comment:
                    current_entry.comment += "\n" + comment
                else:
                    current_entry.comment = comment
            continue

        # Empty line - treat as separator
        if key == "" and value == "" and not comment:
            continue

        # Check for Host directive
        if key.lower() == "host":
            # Save previous entry if exists
            if current_entry is not None:
                entries.append(current_entry)

            # Start new entry
            enabled = True
            host_value = value

            # Check if this is a disabled entry (commented out)
            if line.strip().startswith("#"):
                enabled = False
                # Remove # Host prefix to get the actual host pattern
                host_value = line.strip().lstrip("#").replace("Host", "", 1).strip()

            current_entry = SSHConfigEntry(
                enabled=enabled,
                host=host_value,
                options={},
                comment=current_comment.strip(),
            )
            current_comment = ""
        elif current_entry is not None:
            # Add option to current entry
            if key:
                current_entry.options[key] = value

    # Add the last entry if exists
    if current_entry is not None:
        entries.append(current_entry)

    return entries


def save_ssh_config(
    entries: list[SSHConfigEntry],
) -> Literal["ok", "permission_denied", "error"]:
    """Save SSH config entries to ~/.ssh/config file.

    Args:
        entries: List of SSHConfigEntry objects to save.

    Returns:
        "ok" on success,
        "permission_denied" if cannot write to file,
        "error" for other errors.
    """
    lines = []

    for entry in entries:
        # Write entry comment if exists
        if entry.comment:
            lines.append(entry.comment)

        # Write Host line
        host_line = f"Host {entry.host}"
        if not entry.enabled:
            host_line = "# " + host_line
        lines.append(host_line)

        # Write options
        for key, value in entry.options.items():
            option_line = f"  {key} {value}"
            lines.append(option_line)

        # Add empty line between entries
        lines.append("")

    # Join lines and add trailing newline
    content = "\n".join(lines).rstrip("\n") + "\n"

    # Ensure .ssh directory exists
    try:
        os.makedirs(SSH_CONFIG_DIR, mode=0o700, exist_ok=True)
    except Exception:
        return "error"

    # Write to file
    try:
        with open(SSH_CONFIG_FILE, "w") as f:
            f.write(content)
        # Set proper permissions
        os.chmod(SSH_CONFIG_FILE, 0o600)
        return "ok"
    except PermissionError:
        return "permission_denied"
    except Exception:
        return "error"


@dataclass
class PermissionIssue:
    """Represents a single permission security issue."""

    path: str
    current_mode: int
    expected_mode: int
    description: str


def check_ssh_permissions() -> list[PermissionIssue]:
    """Check SSH directory and files for insecure permissions.

    Returns:
        List of PermissionIssue objects for items that need fixing.
    """
    issues: list[PermissionIssue] = []

    if not os.path.exists(SSH_CONFIG_DIR):
        return issues

    # Check ~/.ssh directory permissions
    try:
        dir_stat = os.stat(SSH_CONFIG_DIR)
        dir_mode = stat.S_IMODE(dir_stat.st_mode)
        if dir_mode != 0o700:
            issues.append(
                PermissionIssue(
                    path=SSH_CONFIG_DIR,
                    current_mode=dir_mode,
                    expected_mode=0o700,
                    description="SSH directory should be accessible only by owner",
                )
            )
    except Exception:
        pass

    # Check files in ~/.ssh directory
    try:
        files = os.listdir(SSH_CONFIG_DIR)
    except Exception:
        return issues

    for filename in files:
        filepath = os.path.join(SSH_CONFIG_DIR, filename)
        if os.path.isdir(filepath):
            continue

        try:
            file_stat = os.stat(filepath)
            file_mode = stat.S_IMODE(file_stat.st_mode)
        except Exception:
            continue

        # Determine expected permissions based on file type
        if filename.endswith(".pub"):
            # Public keys: 644 is acceptable, 600 is also fine
            expected_mode = 0o644
            if file_mode != 0o644 and file_mode != 0o600:
                issues.append(
                    PermissionIssue(
                        path=filepath,
                        current_mode=file_mode,
                        expected_mode=expected_mode,
                        description=f"Public key '{filename}' must be world-readable",
                    )
                )
        elif filename in ("config", "authorized_keys", "known_hosts"):
            # Config and authorized_keys: 600
            expected_mode = 0o600
            if file_mode != 0o600:
                issues.append(
                    PermissionIssue(
                        path=filepath,
                        current_mode=file_mode,
                        expected_mode=expected_mode,
                        description="SSH file must be owner-accessible",
                    )
                )
        else:
            # Private keys: 600 strictly
            expected_mode = 0o600
            if file_mode != 0o600:
                issues.append(
                    PermissionIssue(
                        path=filepath,
                        current_mode=file_mode,
                        expected_mode=expected_mode,
                        description="Private key must be owner-accessible",
                    )
                )

    return issues


def fix_ssh_permissions(issues: list[PermissionIssue]) -> list[str]:
    """Fix SSH permission issues.

    Args:
        issues: List of PermissionIssue objects to fix.

    Returns:
        List of paths that failed to fix.
    """
    failed: list[str] = []

    for issue in issues:
        try:
            os.chmod(issue.path, issue.expected_mode)
        except Exception:
            failed.append(issue.path)

    return failed


def get_available_options() -> list[tuple[str, str]]:
    """Get list of commonly used SSH config options with descriptions."""
    return [
        ("HostName", "The real host name to log into"),
        ("Port", "Port number to connect to"),
        ("User", "Username to use for login"),
        ("IdentityFile", "Path to private key file"),
        ("IdentitiesOnly", "Only use specified identity files"),
        ("StrictHostKeyChecking", "Check host key validity"),
        ("UserKnownHostsFile", "Path to known hosts file"),
        ("ServerAliveInterval", "Keep-alive interval in seconds"),
        ("ServerAliveCountMax", "Max keep-alive attempts"),
        ("ForwardAgent", "Forward SSH agent"),
        ("ForwardX11", "Forward X11 connections"),
        ("Compression", "Enable compression"),
        ("ConnectTimeout", "Connection timeout in seconds"),
        ("ProxyJump", "Jump host for proxy connection"),
        ("LocalForward", "Local port forwarding"),
        ("RemoteForward", "Remote port forwarding"),
    ]
