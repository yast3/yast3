"""User manager widget for GTK4."""

from __future__ import annotations

import grp

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.users import UserEntry, list_users

from mast.gtk4.users.user_list import UserList
from mast.gtk4.users.user_form import UserForm


class UserManager(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self._users: list[UserEntry] = []
        self._groups: list[grp.struct_group] = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        self.user_list = UserList()
        self.user_list.connect("user-selected", self._on_user_selected)
        self.user_list.connect("user-added", self._on_add_user)
        self.append(self.user_list)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.append(separator)

        self.user_form = UserForm()
        self.append(self.user_form)

    def _load_data(self) -> None:
        try:
            self._users = list_users()
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self.user_form.set_groups(self._groups)
            self.user_list.set_users(self._users)
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("Failed to load users: {0}").format(str(e)))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()

    def _on_user_selected(self, _sender, user: UserEntry | None) -> None:
        if user:
            self.user_form._is_new_user = False
            self.user_form._selected_user = user
            self.user_form._fill_user_form(user)
        else:
            self.user_form._clear_form()

    def _on_add_user(self, _sender) -> None:
        self.user_form._on_add_user()