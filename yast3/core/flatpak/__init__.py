"""Flatpak management helpers."""

from yast3.core.flatpak.flatpak import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    install_flatpak_pkexec,
    is_flatpak_installed,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
    remove_flatpak_pkexec,
)

__all__ = [
    "FlatpakRemote",
    "add_flatpak_remote",
    "delete_flatpak_remote",
    "install_flatpak_pkexec",
    "is_flatpak_installed",
    "list_flatpak_remotes",
    "modify_flatpak_remote_url",
    "remove_flatpak_pkexec",
]
