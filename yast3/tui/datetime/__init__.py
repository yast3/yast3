"""Date and Time module package - TUI."""

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.datetime.window import DateTimeWindow


class DateTimeModule(Module):
    def __init__(self):
        super().__init__(_("Date & Time"), "🕐")

    def create_window(self):
        """Create and return the module window screen."""
        return DateTimeWindow()


__all__ = ["DateTimeModule"]
