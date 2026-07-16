"""Packages module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.packages.window import PackagesWindow


class PackagesModule(Module):
    def __init__(self):
        super().__init__(_("Packages"), "🎁")

    def create_window(self) -> Screen:
        """Create and return the packages configuration window."""
        return PackagesWindow()


__all__ = ["PackagesModule"]