"""Packages module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.tui.packages.window import PackagesWindow


class PackagesModule(Module):
    def __init__(self):
        super().__init__(_("Packages"), ("package", "preferences-system"), "🎁")

    def create_window(self) -> Screen:
        """Create and return the packages configuration window."""
        return PackagesWindow()


__all__ = ["PackagesModule"]