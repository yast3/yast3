"""Proxy module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.proxy.window import ProxyWindow


class ProxyModule(Module):
    def __init__(self):
        super().__init__(_("Proxy"), "🌐")

    def create_window(self) -> Screen:
        """Create and return the proxy configuration window."""
        return ProxyWindow()


__all__ = ["ProxyModule"]
