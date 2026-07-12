"""Flatpak module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.flatpak.window import FlatpakWindow


class FlatpakModule(Module):
    def __init__(self):
        super().__init__(_("Flatpak"), ("flatpak", "package-x-generic"))

    def _create_window(self):
        return FlatpakWindow()


__all__ = ["FlatpakModule"]