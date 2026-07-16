"""Hosts file management core logic."""

from mast.core.hosts.hosts import (
    HostEntry,
    load_hosts,
    save_hosts,
)

__all__ = [
    "HostEntry",
    "load_hosts",
    "save_hosts",
]