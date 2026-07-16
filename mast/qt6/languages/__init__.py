"""Languages module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.languages.window import LanguagesWindow


class LanguagesModule(Module):
    def __init__(self):
        super().__init__(_("Languages"), ("language", "preferences-desktop-locale"))

    def _create_window(self):
        return LanguagesWindow()


__all__ = ["LanguagesModule"]