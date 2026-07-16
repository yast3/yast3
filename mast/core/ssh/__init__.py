"""SSH config management core logic."""

from mast.core.ssh.ssh import (
    PermissionIssue,
    SSHConfigEntry,
    SSH_CONFIG_DIR,
    SSH_CONFIG_FILE,
    check_ssh_permissions,
    fix_ssh_permissions,
    get_available_options,
    load_ssh_config,
    save_ssh_config,
)

__all__ = [
    "PermissionIssue",
    "SSHConfigEntry",
    "SSH_CONFIG_DIR",
    "SSH_CONFIG_FILE",
    "check_ssh_permissions",
    "fix_ssh_permissions",
    "get_available_options",
    "load_ssh_config",
    "save_ssh_config",
]