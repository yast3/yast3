"""Date and Time module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.gtk4.module import Module
from yast3.gtk4.datetime.window import DateTimeWindow


class DateTimeModule(Module):
    def __init__(self):
        super().__init__(_("Date & Time"), ("clock", "preferences-system-time"), "🕐")

    def _create_window(self) -> Gtk.Window:
        """Create the date & time module window."""
        return DateTimeWindow()


__all__ = ["DateTimeModule"]
