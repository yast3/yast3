"""Git configuration core logic."""

from yast3.core.git.git import (
    GitConfig,
    get_git_config,
    is_git_installed,
    set_git_config,
)

__all__ = [
    "GitConfig",
    "get_git_config",
    "is_git_installed",
    "set_git_config",
]