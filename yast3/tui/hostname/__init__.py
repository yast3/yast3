"""Hostname module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.tui.hostname.window import HostnameWindow


class HostnameModule(Module):
    def __init__(self):
        super().__init__(_("Hostname"), ("computer", "preferences-system-network"), "💻")

    def create_window(self) -> Screen:
        """Create and return the hostname configuration window."""
        return HostnameWindow()


__all__ = ["HostnameModule"]