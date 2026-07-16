"""Hosts module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.hosts.window import HostsWindow


class HostsModule(Module):
    def __init__(self):
        super().__init__(_("Hosts"), "🌐")

    def create_window(self) -> Screen:
        """Create and return the hosts configuration window."""
        return HostsWindow()


__all__ = ["HostsModule"]