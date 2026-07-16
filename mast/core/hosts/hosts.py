"""Hosts file reading and writing logic."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Literal

HOSTS_FILE = "/etc/hosts"


@dataclass
class HostEntry:
    """Represents a single hosts file entry."""

    enabled: bool
    ip: str
    hostnames: list[str] = field(default_factory=list)
    comment_sep: str = ""  # Separator before comment (e.g., "\t#" or " #")
    comment: str = ""
    editable: bool = True

    def is_pure_comment(self) -> bool:
        """Check if this is a pure comment line (no IP/hostname)."""
        return not self.editable and not self.ip


def _looks_like_ip(string: str) -> bool:
    """Check if a string looks like an IP address."""
    if not string:
        return False

    # Check for IPv4 address (e.g., 127.0.0.1)
    parts = string.split(".")
    if len(parts) == 4:
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            pass

    # Check for IPv6 address
    # IPv6 consists of hex characters (0-9, a-f, A-F) and colons
    # e.g., ::1, 2001:db8::1, fe80::1%eth0
    if ":" in string:
        # Remove interface suffix like %eth0 if present
        addr = string.split("%")[0]
        # Check if it's a valid IPv6 format
        # All characters should be hex digits or colons
        valid_chars = set("0123456789abcdefABCDEF:")
        if all(c in valid_chars for c in addr):
            # Additional check: should have at least one hex segment
            segments = addr.replace("::", ":").split(":")
            # Empty segments are ok for :: but there should be some content
            return any(s for s in segments) or addr == "::"

    return False


def _parse_hostnames_and_comment(rest: str) -> tuple[list[str], str, str]:
    """Parse hostname string into hostnames list, comment separator, and comment.

    Returns:
        (hostnames, comment_sep, comment)
        - hostnames: list of hostname strings
        - comment_sep: separator before comment (e.g., "\t#" or " #")
        - comment: comment content with leading spaces preserved
    """
    if not rest:
        return [], "", ""

    # Find the first # in the original string to preserve leading spaces/tabs
    comment_pos = rest.find("#")

    if comment_pos == -1:
        # No comment, all are hostnames
        return rest.split(), "", ""

    # Extract hostnames part (before #)
    hostnames_str = rest[:comment_pos]
    # Get hostnames (split by whitespace)
    hostnames = hostnames_str.split() if hostnames_str.strip() else []

    # Calculate the separator: everything after last hostname up to #
    # This preserves the exact whitespace before #
    if hostnames:
        # Find where the last hostname ends
        last_hostname = hostnames[-1]
        last_pos = hostnames_str.rfind(last_hostname)
        if last_pos != -1:
            # Separator is from end of last hostname to #
            after_last = hostnames_str[last_pos + len(last_hostname) :]
            comment_sep = after_last + "#"
        else:
            comment_sep = "#"
    else:
        # No hostnames, separator is everything before # plus #
        comment_sep = hostnames_str + "#"

    # Extract comment (after #, preserving leading spaces/tabs)
    comment = rest[comment_pos + 1 :]  # Remove # but keep everything after

    return hostnames, comment_sep, comment


def load_hosts() -> list[HostEntry]:
    """Load hosts from /etc/hosts file.

    Returns:
        List of HostEntry objects.

    Raises:
        PermissionError: If cannot read the file.
        FileNotFoundError: If the file does not exist.
    """
    entries: list[HostEntry] = []

    with open(HOSTS_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        original_line = line.rstrip("\n\r")
        stripped = original_line.strip()

        # Empty line - skip
        if not stripped:
            continue

        # Full comment line (no IP/hostname, just a comment)
        if stripped.startswith("#"):
            content = stripped.lstrip("#")
            # Check if this looks like a valid hosts entry (has IP as first part)
            parts = content.strip().split(None, 1)
            # If no parts or first part doesn't look like an IP, treat as pure comment
            if not parts or not _looks_like_ip(parts[0]):
                entries.append(
                    HostEntry(
                        enabled=True,
                        ip="",
                        hostnames=[],
                        comment_sep="#",
                        comment=content.strip(),
                        editable=False,
                    )
                )
                continue

            # This is a disabled entry (commented-out hosts entry)
            ip = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            hostnames, comment_sep, comment = _parse_hostnames_and_comment(rest)
            entries.append(
                HostEntry(
                    enabled=False,
                    ip=ip,
                    hostnames=hostnames,
                    comment_sep=comment_sep,
                    comment=comment,
                    editable=len(hostnames) > 0,
                )
            )
            continue

        # Normal entry
        parts = stripped.split(None, 1)
        if parts and parts[0]:
            ip = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            hostnames, comment_sep, comment = _parse_hostnames_and_comment(rest)
            entries.append(
                HostEntry(
                    enabled=True,
                    ip=ip,
                    hostnames=hostnames,
                    comment_sep=comment_sep,
                    comment=comment,
                    editable=len(hostnames) > 0,
                )
            )

    return entries


def save_hosts(
    entries: list[HostEntry], use_pkexec: bool = True
) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Save hosts entries to /etc/hosts file.

    Args:
        entries: List of HostEntry objects to save.
        use_pkexec: If True, use pkexec for privilege escalation on permission error.

    Returns:
        "ok" on success,
        "permission_denied" if direct write fails and use_pkexec is False,
        "pkexec_failed" if pkexec authentication fails,
        "error" for other errors.
    """
    lines = []
    for entry in entries:
        if not entry.editable:
            # Pure comment line - just write the comment with original separator
            lines.append(entry.comment_sep + entry.comment)
            continue

        line = ""
        if not entry.enabled:
            line += "# "
        line += entry.ip + "\t" + " ".join(entry.hostnames)
        if entry.comment:
            # Use original comment separator to preserve formatting
            line += entry.comment_sep + entry.comment
        lines.append(line)

    # Add trailing newline
    content = "\n".join(lines) + "\n"

    # Try direct write first
    try:
        with open(HOSTS_FILE, "w") as f:
            f.write(content)
        return "ok"
    except PermissionError:
        if not use_pkexec:
            return "permission_denied"
        # Need root permission - use pkexec
    except Exception:
        return "error"

    # Use pkexec to get root permission
    try:
        # Write to a temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".hosts", delete=False
        ) as tmp:
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
