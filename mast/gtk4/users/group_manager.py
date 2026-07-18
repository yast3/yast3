"""Groups tab widget for GTK4."""

from __future__ import annotations

import grp
import re

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    list_users,
    build_add_group_command,
    build_modify_group_command,
    build_delete_group_command,
    is_system_group,
)
from mast.gtk4.command.action import CommandAction


class GroupManager(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self._groups: list[grp.struct_group] = []
        self._users: list[UserEntry] = []
        self._selected_group: grp.struct_group | None = None
        self._is_new_group = False
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.group_tree = Gtk.TreeView()
        self.group_tree.set_headers_visible(False)
        self.group_tree.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.group_tree.set_margin_start(8)
        self.group_tree.set_margin_top(8)

        column = Gtk.TreeViewColumn()
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "text", 0)
        self.group_tree.append_column(column)

        self.group_store = Gtk.TreeStore(str, object)

        self.group_tree.set_model(self.group_store)
        self.group_tree.get_selection().connect("changed", self._on_group_selected)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.group_tree)
        scrolled.set_vexpand(True)

        left_panel.append(scrolled)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_bottom(8)

        self.add_btn = Gtk.Button(label=_("Add"))
        self.add_btn.connect("clicked", self._on_add_group)
        button_box.append(self.add_btn)

        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.connect("clicked", self._on_delete_group)
        self.delete_btn.set_sensitive(False)
        button_box.append(self.delete_btn)

        left_panel.append(button_box)

        self.append(left_panel)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.append(separator)

        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

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

        right_panel.append(grid)

        save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save_box.set_halign(Gtk.Align.END)
        save_box.set_margin_end(8)
        save_box.set_margin_bottom(8)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.connect("clicked", self._on_save_group)
        self.save_btn.set_sensitive(False)
        save_box.append(self.save_btn)

        right_panel.append(save_box)

        right_panel.set_hexpand(True)
        right_panel.set_vexpand(True)
        self.append(right_panel)

    def _load_data(self) -> None:
        try:
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._users = list_users()
            self._populate_group_tree()
            self._populate_members_list()
            if self._selected_group:
                self._fill_group_form(self._selected_group)
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

    def _populate_group_tree(self) -> None:
        self.group_store.clear()

        system_group_item = self.group_store.append(None, [_("System Groups"), None])
        user_group_item = self.group_store.append(None, [_("User Groups"), None])

        users_iter = None
        for group in self._groups:
            if is_system_group(group):
                tree_iter = self.group_store.append(system_group_item, [group.gr_name, group])
            else:
                tree_iter = self.group_store.append(user_group_item, [group.gr_name, group])
            if group.gr_name == "users":
                users_iter = tree_iter

        self.group_tree.expand_all()

        if users_iter:
            selection = self.group_tree.get_selection()
            selection.select_iter(users_iter)

    def _populate_members_list(self) -> None:
        for cb in self.members_checkbuttons.values():
            self.members_box.remove(cb)
        self.members_checkbuttons.clear()

        for user in self._users:
            cb = Gtk.CheckButton(label=user.username)
            cb.set_tooltip_text(user.full_name)
            self.members_checkbuttons[user.username] = cb
            self.members_box.append(cb)

    def _on_group_selected(self, selection) -> None:
        model, tree_iter = selection.get_selected()
        if tree_iter:
            self._is_new_group = False
            self._selected_group = model.get_value(tree_iter, 1)
            if self._selected_group:
                self._fill_group_form(self._selected_group)
                is_system = is_system_group(self._selected_group)
                self.delete_btn.set_sensitive(not is_system)
                self.save_btn.set_sensitive(not is_system)
            else:
                self.delete_btn.set_sensitive(False)
                self.save_btn.set_sensitive(False)
        else:
            self._selected_group = None
            self._clear_form()
            self.delete_btn.set_sensitive(False)
            self.save_btn.set_sensitive(False)

    def _fill_group_form(self, group: grp.struct_group) -> None:
        self.group_name_edit.set_text(group.gr_name)
        self.group_name_edit.set_editable(False)
        self.gid_label.set_label(str(group.gr_gid))

        for username, cb in self.members_checkbuttons.items():
            user = next(u for u in self._users if u.username == username)
            cb.set_active(user.primary_group == group.gr_name or user.username in group.gr_mem)

    def _clear_form(self) -> None:
        self.group_name_edit.set_text("")
        self.group_name_edit.set_editable(True)
        self.gid_label.set_label("")
        for cb in self.members_checkbuttons.values():
            cb.set_active(False)

    def _on_add_group(self, _button) -> None:
        self._is_new_group = True
        self._selected_group = None
        self.group_tree.get_selection().unselect_all()
        self.group_name_edit.set_editable(True)
        self.group_name_edit.set_text("")
        self.gid_label.set_label("")
        for cb in self.members_checkbuttons.values():
            cb.set_active(False)
        self.delete_btn.set_sensitive(False)
        self.save_btn.set_sensitive(True)
        self.group_name_edit.grab_focus()

    def _on_delete_group(self, _button) -> None:
        if not self._selected_group:
            return

        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        dialog.set_property("secondary-text", _("Are you sure you want to delete group '{0}'?").format(self._selected_group.gr_name))
        dialog.connect("response", self._on_delete_confirm, self._selected_group.gr_name)
        dialog.present()

    def _on_delete_confirm(self, dialog, response_id, group_name) -> None:
        if response_id == Gtk.ResponseType.YES:
            cmd = build_delete_group_command(group_name)
            action = CommandAction(
                text=_("Delete"),
                running_text=_("Deleting..."),
                dialog_title=_("Delete Group"),
                command=cmd,
                success_output=_("Group '{0}' deleted successfully.").format(group_name),
                parent_window=self.get_root(),
            )
            action.connect_finished(self._on_action_finished)
            action.start_action()
        dialog.destroy()

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
            self._load_data()
            self._clear_form()
            self._is_new_group = False
            self.save_btn.set_sensitive(False)
            self.delete_btn.set_sensitive(False)