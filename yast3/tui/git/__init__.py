"""Git module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.tui.git.window import GitWindow


class GitModule(Module):
    def __init__(self):
        super().__init__(_("Git"), ("preferences-git", "settings"), "📝")

    def create_window(self) -> Screen:
        """Create and return the git configuration window."""
        return GitWindow()


__all__ = ["GitModule"]