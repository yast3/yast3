"""Repositories module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.repositories.window import RepositoriesWindow


class RepositoriesModule(Module):
    def __init__(self):
        super().__init__(
            _("Repositories"), ("system-software-install", "package-x-generic")
        )

    def _create_window(self):
        return RepositoriesWindow()


__all__ = ["RepositoriesModule"]