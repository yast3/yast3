"""Hosts module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.qt6.hosts.window import HostsWindow


class HostsModule(Module):
    window: HostsWindow | None = None

    def __init__(self):
        super().__init__(_("Hosts"), ("network", "network-workgroup"), "🌐")

    def launch(self) -> None:
        """Launch the hosts module window."""
        if self.window is None:
            self.window = HostsWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["HostsModule"]