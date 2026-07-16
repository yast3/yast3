"""Date and Time module package - TUI."""

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.datetime.window import DateTimeWindow


class DateTimeModule(Module):
    def __init__(self):
        super().__init__(_("Date & Time"), "🕐")

    def create_window(self):
        """Create and return the module window screen."""
        return DateTimeWindow()


__all__ = ["DateTimeModule"]
