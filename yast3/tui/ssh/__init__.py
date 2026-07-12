"""SSH module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.ssh.window import SSHWindow


class SSHClientModule(Module):
    def __init__(self):
        super().__init__(_("SSH Client"), ("ssh", "network-server"), "🔐")

    def create_window(self) -> Screen:
        """Create and return the SSH configuration window."""
        return SSHWindow()


__all__ = ["SSHClientModule"]