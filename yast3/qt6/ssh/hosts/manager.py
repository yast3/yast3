"""SSH Hosts manager - handles SSH config operations and logic."""

from __future__ import annotations

from typing import Optional, Tuple

from yast3.core.ssh import SSHConfigEntry, load_ssh_config, save_ssh_config


class HostManager:
    """Manages SSH config host operations."""

    @staticmethod
    def load_config() -> Tuple[list[SSHConfigEntry], Optional[str]]:
        """Load SSH config from ~/.ssh/config file.

        Returns:
            Tuple of (entries, error_message). Error message is None on success.
        """
        try:
            entries = load_ssh_config()
            return (entries, None)
        except FileNotFoundError:
            # Config file doesn't exist - that's OK
            return ([], None)
        except PermissionError:
            return ([], "Cannot read SSH config. Check permissions.")
        except Exception as e:
            return ([], f"Failed to load SSH config: {str(e)}")

    @staticmethod
    def save_config(entries: list[SSHConfigEntry]) -> str:
        """Save SSH config to ~/.ssh/config file.

        Returns:
            "ok" on success, "permission_denied" on permission error, "error" otherwise.
        """
        return save_ssh_config(entries)

    @staticmethod
    def create_entry(
        host: str, options: dict = None, enabled: bool = True, editable: bool = True
    ) -> SSHConfigEntry:
        """Create a new SSH config entry."""
        return SSHConfigEntry(
            enabled=enabled, host=host, options=options or {}, editable=editable
        )

    @staticmethod
    def update_entry(
        entry: SSHConfigEntry, new_host: str, new_options: dict
    ) -> SSHConfigEntry:
        """Update an existing SSH config entry."""
        return SSHConfigEntry(
            enabled=entry.enabled,
            host=new_host,
            options=new_options,
            editable=entry.editable,
        )

    @staticmethod
    def can_delete(entry: SSHConfigEntry) -> bool:
        """Check if an entry can be deleted."""
        return not entry.is_default()

    @staticmethod
    def is_default(entry: SSHConfigEntry) -> bool:
        """Check if an entry is the default host entry."""
        return entry.is_default()