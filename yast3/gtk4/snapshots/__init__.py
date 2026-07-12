"""Snapshots module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.gtk4.module import Module
from yast3.gtk4.snapshots.window import SnapshotsWindow


class SnapshotsModule(Module):
    def __init__(self):
        super().__init__(_("Snapshots"), ("camera-photo", "document-save"), "📸")

    def _create_window(self) -> Gtk.Window:
        return SnapshotsWindow()


__all__ = ["SnapshotsModule"]