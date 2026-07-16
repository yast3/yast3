"""Cron job management module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.module import Module
from mast.gtk4.cron.window import CronWindow


class CronModule(Module):
    def __init__(self):
        super().__init__(_("Cron"), ("preferences-system-time", "chronometer", "clock"))

    def _create_window(self) -> Gtk.Window:
        """Create the cron module window."""
        return CronWindow()


__all__ = ["CronModule"]
