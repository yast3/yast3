"""Git module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.git.window import GitWindow


class GitModule(Module):
    def __init__(self):
        super().__init__(_("Git"), "📝")

    def create_window(self) -> Screen:
        """Create and return the git configuration window."""
        return GitWindow()


__all__ = ["GitModule"]