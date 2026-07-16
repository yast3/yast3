"""Date and Time module package - Qt6 GUI."""

from PySide6.QtWidgets import QMainWindow

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.datetime.window import DateTimeWindow


class DateTimeModule(Module):
    def __init__(self):
        super().__init__(_("Date & Time"), ("clock", "preferences-system-time"))

    def _create_window(self) -> QMainWindow:
        """Create the date & time module window."""
        return DateTimeWindow()


__all__ = ["DateTimeModule"]
