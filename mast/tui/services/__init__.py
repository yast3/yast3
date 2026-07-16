"""Services module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.services.window import ServicesWindow


class ServicesModule(Module):
    def __init__(self):
        super().__init__(_("Services"), "🧰")

    def create_window(self) -> Screen:
        """Create and return the services management window."""
        return ServicesWindow()


__all__ = ["ServicesModule"]
