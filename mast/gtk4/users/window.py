"""UI components for the Users & Groups module (GTK4)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.users.user_manager import UserManager
from mast.gtk4.users.group_manager import GroupManager


class UsersWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(960, 640)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)

        self.notebook = Gtk.Notebook()

        self.users_tab = UserManager()
        self.notebook.append_page(self.users_tab, Gtk.Label(label=_("Users")))

        self.groups_tab = GroupManager()
        self.notebook.append_page(self.groups_tab, Gtk.Label(label=_("Groups")))

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)