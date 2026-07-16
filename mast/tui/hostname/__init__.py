"""Hostname module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.hostname.window import HostnameWindow


class HostnameModule(Module):
    def __init__(self):
        super().__init__(_("Hostname"), "💻")

    def create_window(self) -> Screen:
        """Create and return the hostname configuration window."""
        return HostnameWindow()


__all__ = ["HostnameModule"]