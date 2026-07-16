"""Proxy module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.proxy.window import ProxyWindow


class ProxyModule(Module):
    def __init__(self):
        super().__init__(_("Proxy"), "🌐")

    def create_window(self) -> Screen:
        """Create and return the proxy configuration window."""
        return ProxyWindow()


__all__ = ["ProxyModule"]
