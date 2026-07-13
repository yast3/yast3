"""Languages module package - TUI."""

from yast3.core.i18n import _
from yast3.tui.module import Module
from yast3.tui.languages.window import LanguagesWindow


class LanguagesModule(Module):
    def __init__(self):
        super().__init__(_("Languages"), "🌐")

    def create_window(self):
        return LanguagesWindow()


__all__ = ["LanguagesModule"]