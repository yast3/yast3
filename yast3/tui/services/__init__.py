"""Services module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.services.window import ServicesWindow


class ServicesModule(Module):
    def __init__(self):
        super().__init__(_("Services"), ("preferences-system-services", "system-run"), "🧰")

    def create_window(self) -> Screen:
        """Create and return the services management window."""
        return ServicesWindow()


__all__ = ["ServicesModule"]
