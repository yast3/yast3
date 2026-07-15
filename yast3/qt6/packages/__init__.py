"""Packages module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.packages.window import PackagesWindow


class PackagesModule(Module):
    def __init__(self):
        super().__init__(_("Packages"), ("package-manager", "package"))

    def _create_window(self):
        return PackagesWindow()


__all__ = ["PackagesModule"]