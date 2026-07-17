"""Journal module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.module import Module
from mast.gtk4.journal.window import JournalWindow


class JournalModule(Module):
    def __init__(self):
        super().__init__(_("Journal"), ("utilities-system-monitor", "system-log"), experimental=True)

    def _create_window(self) -> Gtk.Window:
        return JournalWindow()


__all__ = ["JournalModule"]
