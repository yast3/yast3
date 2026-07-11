"""Date and Time module package - Qt6 GUI."""

from PySide6.QtWidgets import QMainWindow

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.qt6.datetime.window import DateTimeWindow


class DateTimeModule(Module):
    window: DateTimeWindow | None = None

    def __init__(self):
        super().__init__(_("Date & Time"), ("clock", "preferences-system-time"), "🕐")

    def launch(self, parent: QMainWindow | None = None) -> None:
        """Launch the date & time module window."""
        if self.window is None:
            self.window = DateTimeWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["DateTimeModule"]