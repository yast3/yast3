"""Cron job management module package."""

from yast3.i18n import _
from yast3.module import Module
from yast3.modules.cron.window import CronWindow


class CronModule(Module):
    window: CronWindow | None = None

    def __init__(self):
        super().__init__(_("Cron"), ("preferences-system-time", "chronometer", "clock"))

    def launch(self) -> None:
        if self.window is None:
            self.window = CronWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)

        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        self.window = None


__all__ = ["CronModule"]