"""Repositories module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.gtk4.repositories.window import RepositoriesWindow


class RepositoriesModule(Module):
    window: RepositoriesWindow | None = None

    def __init__(self):
        super().__init__(
            _("Repositories"), ("system-software-install", "package-x-generic"), "📦"
        )

    def launch(self, parent: Gtk.ApplicationWindow | None = None) -> None:
        """Launch the repositories module window."""
        if self.window is None:
            self.window = RepositoriesWindow()
            self.window.set_title(self.name + " — " + _("YaST3"))
            self.window.connect("delete-event", self._on_window_closed)
        self.window.show_all()

    def _on_window_closed(self, window) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["RepositoriesModule"]