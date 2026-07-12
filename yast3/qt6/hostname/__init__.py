"""Hostname module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.hostname.window import HostnameWindow


class HostnameModule(Module):
    def __init__(self):
        super().__init__(_("Hostname"), ("computer", "preferences-system-network"), "💻")

    def _create_window(self):
        return HostnameWindow()


__all__ = ["HostnameModule"]