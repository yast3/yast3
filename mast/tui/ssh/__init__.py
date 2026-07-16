"""SSH module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.ssh.window import SSHWindow


class SSHClientModule(Module):
    def __init__(self):
        super().__init__(_("SSH Client"), "🔐")

    def create_window(self) -> Screen:
        """Create and return the SSH configuration window."""
        return SSHWindow()


__all__ = ["SSHClientModule"]