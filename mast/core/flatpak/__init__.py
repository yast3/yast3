"""Flatpak management helpers."""

from mast.core.flatpak.package import (
    FlatpakPackage,
    install_flatpak_package,
    list_flatpak_packages,
    list_remote_flatpak_packages,
    search_flatpak_packages,
    uninstall_flatpak_package,
)
from mast.core.flatpak.runtime import (
    FlatpakRuntime,
    list_flatpak_runtimes,
    uninstall_flatpak_runtime,
)
from mast.core.flatpak.flatpak import (
    install_flatpak_pkexec,
    is_flatpak_installed,
    remove_flatpak_pkexec,
)
from mast.core.flatpak.remote import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
)

__all__ = [
    "FlatpakPackage",
    "FlatpakRuntime",
    "FlatpakRemote",
    "add_flatpak_remote",
    "delete_flatpak_remote",
    "install_flatpak_pkexec",
    "install_flatpak_package",
    "is_flatpak_installed",
    "list_flatpak_packages",
    "list_remote_flatpak_packages",
    "list_flatpak_remotes",
    "list_flatpak_runtimes",
    "modify_flatpak_remote_url",
    "remove_flatpak_pkexec",
    "search_flatpak_packages",
    "uninstall_flatpak_package",
    "uninstall_flatpak_runtime",
]
