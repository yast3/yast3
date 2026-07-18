"""Group manager widget for GTK4."""

from __future__ import annotations

import grp

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.users import UserEntry, list_users, is_system_group

from mast.gtk4.users.group_list import GroupList
from mast.gtk4.users.group_form import GroupForm


class GroupManager(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self._groups: list[grp.struct_group] = []
        self._users: list[UserEntry] = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        self.group_list = GroupList()
        self.group_list.connect("group-selected", self._on_group_selected)
        self.group_list.connect("group-added", self._on_add_group)
        self.append(self.group_list)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.append(separator)

        self.group_form = GroupForm()
        self.append(self.group_form)

    def _load_data(self) -> None:
        try:
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._users = list_users()
            self.group_form.set_users(self._users)
            self.group_list.set_groups(self._groups)
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("Failed to load groups: {0}").format(str(e)))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()

    def _on_group_selected(self, _sender, group) -> None:
        if group:
            self.group_form._is_new_group = False
            self.group_form._selected_group = group
            self.group_form._fill_group_form(group)
        else:
            self.group_form._clear_form()

    def _on_add_group(self, _sender) -> None:
        self.group_form._on_add_group()