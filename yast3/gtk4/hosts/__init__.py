"""Hosts module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.gtk4.hosts.window import HostsWindow


class HostsModule(Module):
    window: HostsWindow | None = None

    def __init__(self):
        super().__init__(_("Hosts"), ("network", "network-workgroup"), "🌐")

    def launch(self, parent: Gtk.ApplicationWindow | None = None) -> None:
        """Launch the hosts module window."""
        if self.window is None:
            self.window = HostsWindow()
            self.window.set_title(self.name + " — " + _("YaST3"))
            self.window.connect("close-request", self._on_window_closed)
        self.window.present()

    def _on_window_closed(self, window) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["HostsModule"]