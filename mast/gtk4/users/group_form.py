"""Group form widget for GTK4."""

from __future__ import annotations

import grp
import re

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject

from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    build_add_group_command,
    build_modify_group_command,
    is_system_group,
)
from mast.gtk4.command.action import CommandAction


class GroupForm(Gtk.Box):
    __gtype_name__ = "GroupForm"
    group_saved = GObject.Signal("group-saved")
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._users: list[UserEntry] = []
        self._selected_group: grp.struct_group | None = None
        self._is_new_group = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(8)
        grid.set_margin_start(16)
        grid.set_margin_end(16)
        grid.set_margin_top(16)
        grid.set_margin_bottom(16)

        grid.attach(Gtk.Label(label=_("GID")), 0, 0, 1, 1)
        self.gid_label = Gtk.Label(label="")
        grid.attach(self.gid_label, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label=_("Group Name")), 0, 1, 1, 1)
        self.group_name_edit = Gtk.Entry()
        grid.attach(self.group_name_edit, 1, 1, 1, 1)

        members_label = Gtk.Label(label=_("Members"))
        members_label.set_valign(Gtk.Align.START)
        grid.attach(members_label, 0, 2, 1, 1)

        self.members_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.members_checkbuttons: dict[str, Gtk.CheckButton] = {}

        members_scrolled = Gtk.ScrolledWindow()
        members_scrolled.set_child(self.members_box)
        members_scrolled.set_vexpand(True)
        grid.attach(members_scrolled, 1, 2, 1, 1)

        self.append(grid)

        save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save_box.set_halign(Gtk.Align.END)
        save_box.set_margin_end(8)
        save_box.set_margin_bottom(8)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.connect("clicked", self._on_save_group)
        self.save_btn.set_sensitive(False)
        save_box.append(self.save_btn)

        self.append(save_box)

        self.set_hexpand(True)
        self.set_vexpand(True)

    def set_users(self, users: list[UserEntry]) -> None:
        self._users = users
        self._populate_members_list()

    def _populate_members_list(self) -> None:
        for cb in self.members_checkbuttons.values():
            self.members_box.remove(cb)
        self.members_checkbuttons.clear()

        for user in self._users:
            cb = Gtk.CheckButton(label=user.username)
            cb.set_tooltip_text(user.full_name)
            self.members_checkbuttons[user.username] = cb
            self.members_box.append(cb)

    def _fill_group_form(self, group: grp.struct_group) -> None:
        self.group_name_edit.set_text(group.gr_name)
        self.group_name_edit.set_editable(False)
        self.gid_label.set_label(str(group.gr_gid))

        for username, cb in self.members_checkbuttons.items():
            user = next(u for u in self._users if u.username == username)
            cb.set_active(user.primary_group == group.gr_name or user.username in group.gr_mem)

        self.save_btn.set_sensitive(True)

    def _clear_form(self) -> None:
        self.group_name_edit.set_text("")
        self.group_name_edit.set_editable(True)
        self.gid_label.set_label("")
        for cb in self.members_checkbuttons.values():
            cb.set_active(False)
        self.save_btn.set_sensitive(False)

    def _on_add_group(self) -> None:
        self._is_new_group = True
        self._selected_group = None
        self.group_name_edit.set_editable(True)
        self.group_name_edit.set_text("")
        self.gid_label.set_label("")
        for cb in self.members_checkbuttons.values():
            cb.set_active(False)
        self.save_btn.set_sensitive(True)
        self.group_name_edit.grab_focus()

    def _on_save_group(self, _button) -> None:
        group_name = self.group_name_edit.get_text().strip()
        if not group_name:
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("Group name cannot be empty"))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
            return

        if self._is_new_group and not re.match(r"^[a-z][a-z0-9_-]*$", group_name):
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("Group name must start with a lowercase letter and can only contain lowercase letters, digits, hyphens, and underscores."))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
            return

        selected_users = []
        for username, cb in self.members_checkbuttons.items():
            if cb.get_active():
                selected_users.append(username)

        if self._is_new_group:
            cmd = build_add_group_command(group_name)
            success_msg = _("Group '{0}' created successfully.").format(group_name)
            dialog_title = _("Create Group")
        else:
            cmd = build_modify_group_command(group_name, selected_users)
            success_msg = _("Group '{0}' updated successfully.").format(group_name)
            dialog_title = _("Update Group")

        action = CommandAction(
            text=_("Save"),
            running_text=_("Saving..."),
            dialog_title=dialog_title,
            command=cmd,
            success_output=success_msg,
            parent_window=self.get_root(),
        )
        action.connect_finished(self._on_action_finished)
        action.start_action()

    def _on_action_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._clear_form()
            self._is_new_group = False
            self.save_btn.set_sensitive(False)
            self.group_saved.emit()