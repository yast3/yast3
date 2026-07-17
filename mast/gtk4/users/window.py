"""UI components for the Users & Groups module (GTK4)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.users.users_tab import UsersTab
from mast.gtk4.users.groups_tab import GroupsTab


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

        self.users_tab = UsersTab()
        self.notebook.append_page(self.users_tab, Gtk.Label(label=_("Users")))

        self.groups_tab = GroupsTab()
        self.notebook.append_page(self.groups_tab, Gtk.Label(label=_("Groups")))

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)