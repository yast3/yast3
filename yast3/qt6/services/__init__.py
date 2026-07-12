"""Services module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.services.window import ServicesWindow


class ServicesModule(Module):
    def __init__(self):
        super().__init__(_("Services"), ("preferences-system-services", "system-run"))

    def _create_window(self):
        return ServicesWindow()


__all__ = ["ServicesModule"]