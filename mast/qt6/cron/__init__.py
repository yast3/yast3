"""Cron job management module package - Qt6 GUI."""

from PySide6.QtWidgets import QMainWindow

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.cron.window import CronWindow


class CronModule(Module):
    def __init__(self):
        super().__init__(_("Cron"), ("preferences-system-time", "chronometer", "clock"))

    def _create_window(self) -> QMainWindow:
        """Create the cron module window."""
        return CronWindow()


__all__ = ["CronModule"]
