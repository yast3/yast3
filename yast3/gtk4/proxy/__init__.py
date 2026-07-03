"""Proxy module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.gtk4.proxy.window import ProxyWindow


class ProxyModule(Module):
    window: ProxyWindow | None = None

    def __init__(self):
        super().__init__(_("Proxy"), ("network-server", "preferences-system-network"), "🌐")

    def launch(self, parent: Gtk.ApplicationWindow | None = None) -> None:
        """Launch the proxy module window."""
        if self.window is None:
            self.window = ProxyWindow()
            self.window.set_title(self.name + " — " + _("YaST3"))
            self.window.connect("close-request", self._on_window_closed)
        self.window.present()

    def _on_window_closed(self, window) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["ProxyModule"]
