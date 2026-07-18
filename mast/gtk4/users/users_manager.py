"""Users tab widget for GTK4."""

from __future__ import annotations

import grp
import os
import re

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    list_users,
    build_add_user_command,
    build_modify_user_command,
    build_delete_user_command,
    build_set_password_command,
    is_user_deletable,
)
from mast.gtk4.command.action import CommandAction


class UsersManager(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self._users: list[UserEntry] = []
        self._groups: list[grp.struct_group] = []
        self._selected_user: UserEntry | None = None
        self._is_new_user = False
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.user_list = Gtk.ListBox()
        self.user_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.user_list.connect("row-selected", self._on_user_selected)
        self.user_list.set_margin_start(8)
        self.user_list.set_margin_top(8)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.user_list)
        scrolled.set_vexpand(True)

        left_panel.append(scrolled)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_bottom(8)

        self.add_btn = Gtk.Button(label=_("Add"))
        self.add_btn.connect("clicked", self._on_add_user)
        button_box.append(self.add_btn)

        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.connect("clicked", self._on_delete_user)
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

        grid.attach(Gtk.Label(label=_("UID")), 0, 0, 1, 1)
        self.uid_edit = Gtk.Entry()
        self.uid_edit.set_editable(False)
        grid.attach(self.uid_edit, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label=_("Username")), 0, 1, 1, 1)
        self.username_edit = Gtk.Entry()
        self.username_edit.set_editable(False)
        self.username_edit.connect("changed", self._on_username_changed)
        grid.attach(self.username_edit, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label=_("Display Name")), 0, 3, 1, 1)
        self.full_name_edit = Gtk.Entry()
        self.full_name_edit.set_placeholder_text(_("Full name"))
        grid.attach(self.full_name_edit, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label=_("Home Directory")), 0, 4, 1, 1)
        self.home_dir_edit = Gtk.Entry()
        self.home_dir_edit.set_placeholder_text(_("/home/username"))
        grid.attach(self.home_dir_edit, 1, 4, 1, 1)

        grid.attach(Gtk.Label(label=_("Shell")), 0, 5, 1, 1)
        self.shell_edit = Gtk.Entry()
        self.shell_edit.set_placeholder_text(_("/bin/bash"))
        grid.attach(self.shell_edit, 1, 5, 1, 1)

        grid.attach(Gtk.Label(label=_("Password")), 0, 6, 1, 1)
        self.password_edit = Gtk.Entry()
        self.password_edit.set_visibility(False)
        self.password_edit.set_placeholder_text(_("Leave empty to skip"))
        grid.attach(self.password_edit, 1, 6, 1, 1)

        grid.attach(Gtk.Label(label=_("Primary Group")), 0, 7, 1, 1)
        self.primary_group_combo = Gtk.ComboBoxText()
        grid.attach(self.primary_group_combo, 1, 7, 1, 1)

        groups_label = Gtk.Label(label=_("Additional Groups"))
        groups_label.set_valign(Gtk.Align.START)
        grid.attach(groups_label, 0, 8, 1, 1)

        self.groups_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.groups_checkbuttons: dict[str, Gtk.CheckButton] = {}

        groups_scrolled = Gtk.ScrolledWindow()
        groups_scrolled.set_child(self.groups_box)
        groups_scrolled.set_vexpand(True)

        grid.attach(groups_scrolled, 1, 8, 1, 1)

        right_panel.append(grid)

        save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save_box.set_halign(Gtk.Align.END)
        save_box.set_margin_end(8)
        save_box.set_margin_bottom(8)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.connect("clicked", self._on_save_user)
        self.save_btn.set_sensitive(False)
        save_box.append(self.save_btn)

        right_panel.append(save_box)

        right_panel.set_hexpand(True)
        right_panel.set_vexpand(True)
        self.append(right_panel)

    def _load_data(self) -> None:
        try:
            self._users = list_users()
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._populate_groups_list()
            self._populate_user_list()
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

    def _populate_user_list(self) -> None:
        for row in self.user_list:
            self.user_list.remove(row)

        current_username = None
        try:
            current_username = os.getlogin()
        except Exception:
            pass

        selected_row = None
        for row_index, user in enumerate(self._users):
            list_row = Gtk.ListBoxRow()
            list_row.set_child(Gtk.Label(label=user.username))
            list_row.user_data = user
            self.user_list.append(list_row)
            if current_username and user.username == current_username:
                selected_row = list_row

        if selected_row:
            self.user_list.select_row(selected_row)

    def _populate_groups_list(self) -> None:
        for cb in self.groups_checkbuttons.values():
            self.groups_box.remove(cb)
        self.groups_checkbuttons.clear()

        self.primary_group_combo.remove_all()

        for group in self._groups:
            cb = Gtk.CheckButton(label=group.gr_name)
            self.groups_checkbuttons[group.gr_name] = cb
            self.groups_box.append(cb)

            self.primary_group_combo.append_text(group.gr_name)

    def _on_user_selected(self, _listbox, row: Gtk.ListBoxRow | None) -> None:
        if row:
            self._is_new_user = False
            self._selected_user = getattr(row, "user_data", None)
            if self._selected_user:
                self._fill_user_form(self._selected_user)
                self.delete_btn.set_sensitive(is_user_deletable(self._selected_user))
            else:
                self.delete_btn.set_sensitive(False)
            self.save_btn.set_sensitive(True)
        else:
            self._selected_user = None
            self._clear_form()
            self.delete_btn.set_sensitive(False)
            self.save_btn.set_sensitive(False)

    def _fill_user_form(self, user: UserEntry) -> None:
        is_root = user.uid == 0

        self.uid_edit.set_text(str(user.uid))
        self.username_edit.set_text(user.username)
        self.full_name_edit.set_text(user.full_name)
        self.home_dir_edit.set_text(user.home_dir)
        self.shell_edit.set_text(user.shell)
        self.password_edit.set_text("")

        self.primary_group_combo.set_active(0)
        model = self.primary_group_combo.get_model()
        for i in range(len(model)):
            if model[i][0] == user.primary_group:
                self.primary_group_combo.set_active(i)
                break

        for group_name, cb in self.groups_checkbuttons.items():
            cb.set_active(group_name in user.groups)

        self.full_name_edit.set_editable(not is_root)
        self.home_dir_edit.set_editable(not is_root)
        self.shell_edit.set_editable(not is_root)
        self.primary_group_combo.set_sensitive(not is_root)

    def _clear_form(self) -> None:
        self.username_edit.set_text("")
        self.full_name_edit.set_text("")
        self.home_dir_edit.set_text("")
        self.shell_edit.set_text("/bin/bash")
        self.primary_group_combo.set_active(0)
        self.password_edit.set_text("")
        for cb in self.groups_checkbuttons.values():
            cb.set_active(False)

    def _on_username_changed(self, _entry) -> None:
        username = self.username_edit.get_text().strip()
        home_dir = self.home_dir_edit.get_text().strip()
        if not home_dir or home_dir.startswith("/home/"):
            self.home_dir_edit.set_text(f"/home/{username}")

    def _on_add_user(self, _button) -> None:
        self._is_new_user = True
        self._selected_user = None
        self.user_list.unselect_all()
        self.uid_edit.set_text("")
        self.username_edit.set_editable(True)
        self.username_edit.set_text("")
        self.full_name_edit.set_text("")
        self.home_dir_edit.set_text("")
        self.shell_edit.set_text("/bin/bash")
        model = self.primary_group_combo.get_model()
        for i in range(len(model)):
            if model[i][0] == "users":
                self.primary_group_combo.set_active(i)
                break
        else:
            self.primary_group_combo.set_active(0)
        self.password_edit.set_text("")
        for cb in self.groups_checkbuttons.values():
            cb.set_active(False)
        self.delete_btn.set_sensitive(False)
        self.save_btn.set_sensitive(True)
        self.username_edit.grab_focus()

    def _on_delete_user(self, _button) -> None:
        if not self._selected_user:
            return

        if not is_user_deletable(self._selected_user):
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("This user cannot be deleted."))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
            return

        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        dialog.set_property("secondary-text", _("Are you sure you want to delete user '{0}'?").format(self._selected_user.username))
        dialog.connect("response", self._on_delete_confirm, self._selected_user.username)
        dialog.present()

    def _on_delete_confirm(self, dialog, response_id, username) -> None:
        if response_id == Gtk.ResponseType.YES:
            cmd = build_delete_user_command(username)
            action = CommandAction(
                text=_("Delete"),
                running_text=_("Deleting..."),
                dialog_title=_("Delete User"),
                command=cmd,
                success_output=_("User '{0}' deleted successfully.").format(username),
                parent_window=self.get_root(),
            )
            action.connect_finished(self._on_action_finished)
            action.start_action()
        dialog.destroy()

    def _on_save_user(self, _button) -> None:
        username = self.username_edit.get_text().strip()
        if not username:
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("Username cannot be empty"))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
            return

        if self._is_new_user:
            if not re.match(r"^[a-z][a-z0-9_-]*$", username):
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_root(),
                    modal=True,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Error"),
                )
                dialog.set_property("secondary-text", _("Username must start with a lowercase letter and can only contain lowercase letters, digits, hyphens, and underscores."))
                dialog.connect("response", lambda d, r: d.destroy())
                dialog.present()
                return

        full_name = self.full_name_edit.get_text().strip()
        home_dir = self.home_dir_edit.get_text().strip()
        shell = self.shell_edit.get_text().strip() or "/bin/bash"
        password = self.password_edit.get_text().strip()
        primary_group = self.primary_group_combo.get_active_text() or ""

        selected_groups = []
        for group_name, cb in self.groups_checkbuttons.items():
            if cb.get_active():
                selected_groups.append(group_name)

        if self._is_new_user:
            cmd = build_add_user_command(
                username=username,
                full_name=full_name,
                home_dir=home_dir,
                shell=shell,
                groups=selected_groups,
                primary_group=primary_group,
            )
            success_msg = _("User '{0}' created successfully.").format(username)
            dialog_title = _("Create User")
        else:
            cmd = build_modify_user_command(
                username=username,
                full_name=full_name,
                home_dir=home_dir,
                shell=shell,
                groups=selected_groups,
                primary_group=primary_group,
            )
            success_msg = _("User '{0}' updated successfully.").format(username)
            dialog_title = _("Update User")

        action = CommandAction(
            text=_("Save"),
            running_text=_("Saving..."),
            dialog_title=dialog_title,
            command=cmd,
            success_output=success_msg,
            parent_window=self.get_root(),
        )
        action.connect_finished(lambda s, e, o: self._on_user_action_finished(s, e, o, username, password))
        action.start_action()

    def _on_user_action_finished(self, success: bool, error: str, stdout: str, username: str, password: str) -> None:
        if success and password:
            cmd = build_set_password_command(username, password)
            action = CommandAction(
                text=_("Set Password"),
                running_text=_("Setting password..."),
                dialog_title=_("Set Password"),
                command=cmd,
                success_output=_("Password set successfully."),
                parent_window=self.get_root(),
            )
            action.connect_finished(lambda s, e, o, u=username: self._on_action_finished(s, e, o, u))
            action.start_action()
        else:
            self._on_action_finished(success, error, stdout, username)

    def _on_action_finished(self, success: bool, _error: str, _stdout: str, username: str = "") -> None:
        if success:
            self._load_data()
            self.username_edit.set_editable(False)
            self._is_new_user = False
            if username:
                for row in self.user_list:
                    if getattr(row, "user_data", None) and row.user_data.username == username:
                        self.user_list.select_row(row)
                        break