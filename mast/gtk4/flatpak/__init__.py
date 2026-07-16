"""Flatpak module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.module import Module
from mast.gtk4.flatpak.window import FlatpakWindow


class FlatpakModule(Module):
    def __init__(self):
        super().__init__(_("Flatpak"), ("flatpak", "package-x-generic"))

    def _create_window(self) -> Gtk.Window:
        return FlatpakWindow()


__all__ = ["FlatpakModule"]