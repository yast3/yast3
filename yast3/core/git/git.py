"""Git configuration reading and writing logic."""

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitConfig:
    """Represents Git user configuration."""

    user_name: str = ""
    user_email: str = ""
    user_signingkey: str = ""
    core_editor: str = ""
    core_autocrlf: str = ""
    core_safecrlf: str = ""
    commit_template: str = ""
    commit_gpgsign: bool = False
    merge_conflictstyle: str = ""
    pull_rebase: str = ""
    color_ui: bool = True
    init_defaultbranch: str = ""
    credential_helper: str = ""


def _get_config_value(key: str) -> Optional[str]:
    """Get a single Git config value."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def _get_config_bool(key: str, default: bool = False) -> bool:
    """Get a boolean Git config value."""
    value = _get_config_value(key)
    if value is None:
        return default
    return value.lower() in ("true", "yes", "1")


def get_git_config() -> GitConfig:
    """Get current Git user configuration.

    Returns:
        GitConfig object with all configuration fields.
    """
    config = GitConfig()

    config.user_name = _get_config_value("user.name") or ""
    config.user_email = _get_config_value("user.email") or ""
    config.user_signingkey = _get_config_value("user.signingkey") or ""
    config.core_editor = _get_config_value("core.editor") or ""
    config.core_autocrlf = _get_config_value("core.autocrlf") or ""
    config.core_safecrlf = _get_config_value("core.safecrlf") or ""
    config.commit_template = _get_config_value("commit.template") or ""
    config.commit_gpgsign = _get_config_bool("commit.gpgsign")
    config.merge_conflictstyle = _get_config_value("merge.conflictstyle") or ""
    config.pull_rebase = _get_config_value("pull.rebase") or ""
    config.color_ui = _get_config_bool("color.ui", True)
    config.init_defaultbranch = _get_config_value("init.defaultbranch") or ""
    config.credential_helper = _get_config_value("credential.helper") or ""

    return config


def _set_config_value(key: str, value: str) -> bool:
    """Set a single Git config value."""
    try:
        subprocess.run(
            ["git", "config", "--global", key, value],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except Exception:
        return False


def _set_config_bool(key: str, value: bool) -> bool:
    """Set a boolean Git config value."""
    return _set_config_value(key, "true" if value else "false")


def _unset_config_value(key: str) -> bool:
    """Unset a Git config value."""
    try:
        subprocess.run(
            ["git", "config", "--global", "--unset", key],
            capture_output=True,
            text=True,
            check=False,
        )
        return True
    except Exception:
        return False


def set_git_config(config: GitConfig) -> bool:
    """Set Git user configuration.

    Args:
        config: GitConfig object with configuration values to set.

    Returns:
        True on success, False on failure.
    """
    try:
        # User settings
        if config.user_name:
            if not _set_config_value("user.name", config.user_name):
                return False
        if config.user_email:
            if not _set_config_value("user.email", config.user_email):
                return False
        if config.user_signingkey:
            if not _set_config_value("user.signingkey", config.user_signingkey):
                return False
        elif _get_config_value("user.signingkey"):
            _unset_config_value("user.signingkey")

        # Core settings
        if config.core_editor:
            if not _set_config_value("core.editor", config.core_editor):
                return False
        elif _get_config_value("core.editor"):
            _unset_config_value("core.editor")

        if config.core_autocrlf:
            if not _set_config_value("core.autocrlf", config.core_autocrlf):
                return False
        elif _get_config_value("core.autocrlf"):
            _unset_config_value("core.autocrlf")

        if config.core_safecrlf:
            if not _set_config_value("core.safecrlf", config.core_safecrlf):
                return False
        elif _get_config_value("core.safecrlf"):
            _unset_config_value("core.safecrlf")

        # Commit settings
        if config.commit_template:
            if not _set_config_value("commit.template", config.commit_template):
                return False
        elif _get_config_value("commit.template"):
            _unset_config_value("commit.template")

        if not _set_config_bool("commit.gpgsign", config.commit_gpgsign):
            return False

        # Merge settings
        if config.merge_conflictstyle:
            if not _set_config_value("merge.conflictstyle", config.merge_conflictstyle):
                return False
        elif _get_config_value("merge.conflictstyle"):
            _unset_config_value("merge.conflictstyle")

        # Pull settings
        if config.pull_rebase:
            if not _set_config_value("pull.rebase", config.pull_rebase):
                return False
        elif _get_config_value("pull.rebase"):
            _unset_config_value("pull.rebase")

        # Color settings
        if not _set_config_bool("color.ui", config.color_ui):
            return False

        # Init settings
        if config.init_defaultbranch:
            if not _set_config_value("init.defaultbranch", config.init_defaultbranch):
                return False
        elif _get_config_value("init.defaultbranch"):
            _unset_config_value("init.defaultbranch")

        # Credential settings
        if config.credential_helper:
            if not _set_config_value("credential.helper", config.credential_helper):
                return False
        elif _get_config_value("credential.helper"):
            _unset_config_value("credential.helper")

        return True
    except Exception:
        return False


def is_git_installed() -> bool:
    """Check if Git is installed on the system.

    Returns:
        True if Git is installed, False otherwise.
    """
    try:
        subprocess.run(["which", "git"], capture_output=True, text=True, check=True)
        return True
    except Exception:
        return False
