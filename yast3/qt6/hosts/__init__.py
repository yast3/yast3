"""Hosts module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.hosts.window import HostsWindow


class HostsModule(Module):
    def __init__(self):
        super().__init__(_("Hosts"), ("network", "network-workgroup"), "🌐")

    def _create_window(self):
        return HostsWindow()


__all__ = ["HostsModule"]