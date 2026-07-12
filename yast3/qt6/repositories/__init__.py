"""Repositories module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.qt6.module import Module
from yast3.qt6.repositories.window import RepositoriesWindow


class RepositoriesModule(Module):
    def __init__(self):
        super().__init__(
            _("Repositories"), ("system-software-install", "package-x-generic"), "📦"
        )

    def _create_window(self):
        return RepositoriesWindow()


__all__ = ["RepositoriesModule"]