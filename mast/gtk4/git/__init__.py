"""Git module package - GTK4 GUI."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.module import Module
from mast.gtk4.git.window import GitWindow


class GitModule(Module):
    def __init__(self):
        super().__init__(_("Git"), ("preferences-git", "settings"), experimental=True)

    def _create_window(self) -> Gtk.Window:
        return GitWindow()


__all__ = ["GitModule"]