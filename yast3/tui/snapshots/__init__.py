"""Snapshots module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.snapshots.window import SnapshotsWindow


class SnapshotsModule(Module):
    def __init__(self):
        super().__init__(_("Snapshots"), "📸")

    def create_window(self) -> Screen:
        """Create and return the snapshots management window."""
        return SnapshotsWindow()


__all__ = ["SnapshotsModule"]
