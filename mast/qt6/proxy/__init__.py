"""Proxy module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.proxy.window import ProxyWindow


class ProxyModule(Module):
    def __init__(self):
        super().__init__(_("Proxy"), ("network-server", "preferences-system-network"))

    def _create_window(self):
        return ProxyWindow()


__all__ = ["ProxyModule"]