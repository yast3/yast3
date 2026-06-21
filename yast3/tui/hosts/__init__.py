"""Hosts module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.tui.hosts.window import HostsWindow


class HostsModule(Module):
    def __init__(self):
        super().__init__(_("Hosts"), ("network", "network-workgroup"), "🌐")

    def create_window(self) -> Screen:
        """Create and return the hosts configuration window."""
        return HostsWindow()


__all__ = ["HostsModule"]