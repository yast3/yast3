"""Hostname module package."""

from yast3.i18n import _
from yast3.module import Module
from yast3.modules.hostname.window import HostnameWindow


class HostnameModule(Module):
    window: HostnameWindow | None = None

    def __init__(self):
        super().__init__(_("Hostname"), ("computer", "preferences-system-network"))

    def launch(self) -> None:
        """Launch the hostname module window."""
        if self.window is None:
            self.window = HostnameWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["HostnameModule"]
