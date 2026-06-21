"""Repositories module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.tui.repositories.window import RepositoriesWindow


class RepositoriesModule(Module):
    def __init__(self):
        super().__init__(_("Repositories"), ("package", "preferences-system"), "📦")

    def create_window(self) -> Screen:
        """Create and return the repositories configuration window."""
        return RepositoriesWindow()


__all__ = ["RepositoriesModule"]