"""Snapshots module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.snapshots.window import SnapshotsWindow


class SnapshotsModule(Module):
    def __init__(self):
        super().__init__(_("Snapshots"), ("camera-photo", "document-save"))

    def _create_window(self):
        return SnapshotsWindow()


__all__ = ["SnapshotsModule"]