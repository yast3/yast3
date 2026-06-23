"""Hostname management core logic."""

from yast3.core.hostname.hostname import (
    HostnameInfo,
    find_localhost_lines,
    get_current_hostname,
    load_hosts_file,
    set_hostname,
    update_hosts_with_hostname,
)

__all__ = [
    "HostnameInfo",
    "find_localhost_lines",
    "get_current_hostname",
    "load_hosts_file",
    "set_hostname",
    "update_hosts_with_hostname",
]