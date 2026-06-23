"""Packages module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.gtk4.packages.window import PackagesWindow


class PackagesModule(Module):
    window: PackagesWindow | None = None

    def __init__(self):
        super().__init__(_("Packages"), ("package-manager", "package"), "🎁")

    def launch(self, parent: Gtk.ApplicationWindow | None = None) -> None:
        """Launch the packages module window."""
        if self.window is None:
            self.window = PackagesWindow()
            self.window.set_title(self.name + " — " + _("YaST3"))
            self.window.connect("delete-event", self._on_window_closed)
        self.window.show_all()

    def _on_window_closed(self, window) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["PackagesModule"]