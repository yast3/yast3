"""Proxy module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.proxy.window import ProxyWindow


class ProxyModule(Module):
    def __init__(self):
        super().__init__(_("Proxy"), ("network-server", "preferences-system-network"), "🌐")

    def _create_window(self):
        return ProxyWindow()


__all__ = ["ProxyModule"]