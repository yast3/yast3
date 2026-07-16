"""Git module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.git.window import GitWindow


class GitModule(Module):
    def __init__(self):
        super().__init__(_("Git"), ("preferences-git", "settings"), experimental=True)

    def _create_window(self):
        return GitWindow()


__all__ = ["GitModule"]