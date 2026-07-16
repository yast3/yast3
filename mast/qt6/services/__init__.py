"""Services module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.services.window import ServicesWindow


class ServicesModule(Module):
    def __init__(self):
        super().__init__(_("Services"), ("preferences-system-services", "system-run"))

    def _create_window(self):
        return ServicesWindow()


__all__ = ["ServicesModule"]