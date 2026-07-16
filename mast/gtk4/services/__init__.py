"""Services module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.module import Module
from mast.gtk4.services.window import ServicesWindow


class ServicesModule(Module):
    def __init__(self):
        super().__init__(_("Services"), ("preferences-system-services", "system-run"))

    def _create_window(self) -> Gtk.Window:
        return ServicesWindow()


__all__ = ["ServicesModule"]