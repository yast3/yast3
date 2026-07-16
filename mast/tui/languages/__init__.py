"""Languages module package - TUI."""

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.languages.window import LanguagesWindow


class LanguagesModule(Module):
    def __init__(self):
        super().__init__(_("Languages"), "🌐")

    def create_window(self):
        return LanguagesWindow()


__all__ = ["LanguagesModule"]