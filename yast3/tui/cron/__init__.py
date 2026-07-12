"""Cron module package - TUI."""

from textual.screen import Screen

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.cron.window import CronWindow


class CronModule(Module):
    def __init__(self):
        super().__init__(_("Cron"), "⏰")

    def create_window(self) -> Screen:
        """Create and return the cron configuration window."""
        return CronWindow()


__all__ = ["CronModule"]
