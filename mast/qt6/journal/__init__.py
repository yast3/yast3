"""Journal module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.journal.window import JournalWindow


class JournalModule(Module):
    def __init__(self):
        super().__init__(_("Journal"), ("utilities-system-monitor", "system-log"), experimental=True)

    def _create_window(self):
        return JournalWindow()


__all__ = ["JournalModule"]
