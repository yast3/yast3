"""Hosts module package."""

from ...module import Module

from .window import HostsWindow


class HostsModule(Module):
    window: HostsWindow | None = None

    def __init__(self):
        super().__init__(_("Hosts"), ("network", "network-workgroup"))

    def launch(self) -> None:
        """Launch the hosts module window."""
        if self.window is None:
            self.window = HostsWindow()
            self.window.setWindowTitle(self.name + ' — ' + _("YaST3"))
        self.window.show()
        self.window.activateWindow()


__all__ = ['HostsModule']