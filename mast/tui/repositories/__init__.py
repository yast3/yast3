"""Repositories module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.repositories.window import RepositoriesWindow


class RepositoriesModule(Module):
    def __init__(self):
        super().__init__(_("Repositories"), "📦")

    def create_window(self) -> Screen:
        """Create and return the repositories configuration window."""
        return RepositoriesWindow()


__all__ = ["RepositoriesModule"]