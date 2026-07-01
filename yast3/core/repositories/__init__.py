"""Repository management core logic."""

from yast3.core.repositories.repos import (
    delete_repo_entry,
    load_repos,
    parse_repo_file,
    RepoEntry,
    save_repo_entry,
)
from yast3.core.repositories.mirrors import switch_mirror

__all__ = [
    "delete_repo_entry",
    "load_repos",
    "parse_repo_file",
    "RepoEntry",
    "save_repo_entry",
    "switch_mirror",
]