"""User form widget for GTK4."""

from __future__ import annotations

import grp
import re

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject

from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    build_add_user_command,
    build_modify_user_command,
    build_set_password_command,
)
from mast.gtk4.command.action import CommandAction


class UserForm(Gtk.Box):
    __gtype_name__ = "UserForm"
    user_saved = GObject.Signal("user-saved")
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._groups: list[grp.struct_group] = []
        self._selected_user: UserEntry | None = None
        self._is_new_user = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(8)
        grid.set_margin_start(16)
        grid.set_margin_end(16)
        grid.set_margin_top(16)
        grid.set_margin_bottom(16)

        grid.attach(Gtk.Label(label=_("UID")), 0, 0, 1, 1)
        self.uid_edit = Gtk.Entry()
        self.uid_edit.set_sensitive(False)
        grid.attach(self.uid_edit, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label=_("Username")), 0, 1, 1, 1)
        self.username_edit = Gtk.Entry()
        self.username_edit.set_sensitive(False)
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

        self.append(grid)

        save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save_box.set_halign(Gtk.Align.END)
        save_box.set_margin_end(8)
        save_box.set_margin_bottom(8)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.connect("clicked", self._on_save_user)
        self.save_btn.set_sensitive(False)
        save_box.append(self.save_btn)

        self.append(save_box)

        self.set_hexpand(True)
        self.set_vexpand(True)

    def set_groups(self, groups: list[grp.struct_group]) -> None:
        self._groups = groups
        self._populate_groups_list()

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

    def _fill_user_form(self, user: UserEntry) -> None:
        is_root = user.uid == 0
        is_system_user = user.uid > 0 and user.uid < 1000

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

        if is_system_user:
            self.full_name_edit.set_sensitive(False)
            self.home_dir_edit.set_sensitive(False)
            self.shell_edit.set_sensitive(False)
            self.password_edit.set_sensitive(False)
            self.primary_group_combo.set_sensitive(False)
            for cb in self.groups_checkbuttons.values():
                cb.set_sensitive(False)
            self.save_btn.set_sensitive(False)
        elif is_root:
            self.full_name_edit.set_sensitive(False)
            self.home_dir_edit.set_sensitive(False)
            self.shell_edit.set_sensitive(False)
            self.password_edit.set_sensitive(True)
            self.primary_group_combo.set_sensitive(False)
            for cb in self.groups_checkbuttons.values():
                cb.set_sensitive(False)
            self.save_btn.set_sensitive(True)
        else:
            self.full_name_edit.set_sensitive(True)
            self.home_dir_edit.set_sensitive(True)
            self.shell_edit.set_sensitive(True)
            self.password_edit.set_sensitive(True)
            self.primary_group_combo.set_sensitive(True)
            for cb in self.groups_checkbuttons.values():
                cb.set_sensitive(True)
            self.save_btn.set_sensitive(True)

    def _clear_form(self) -> None:
        self.username_edit.set_text("")
        self.full_name_edit.set_text("")
        self.home_dir_edit.set_text("")
        self.shell_edit.set_text("/bin/bash")
        self.primary_group_combo.set_active(0)
        self.password_edit.set_text("")
        for cb in self.groups_checkbuttons.values():
            cb.set_active(False)
        self.save_btn.set_sensitive(False)

    def _on_username_changed(self, _entry) -> None:
        username = self.username_edit.get_text().strip()
        home_dir = self.home_dir_edit.get_text().strip()
        if not home_dir or home_dir.startswith("/home/"):
            self.home_dir_edit.set_text(f"/home/{username}")

    def _on_add_user(self) -> None:
        self._is_new_user = True
        self._selected_user = None
        self.uid_edit.set_text("")
        self.username_edit.set_sensitive(True)
        self.username_edit.set_text("")
        self.full_name_edit.set_text("")
        self.full_name_edit.set_sensitive(True)
        self.home_dir_edit.set_text("")
        self.home_dir_edit.set_sensitive(True)
        self.shell_edit.set_text("/bin/bash")
        self.shell_edit.set_sensitive(True)
        self.password_edit.set_text("")
        self.password_edit.set_sensitive(True)
        self.primary_group_combo.set_sensitive(True)
        model = self.primary_group_combo.get_model()
        for i in range(len(model)):
            if model[i][0] == "users":
                self.primary_group_combo.set_active(i)
                break
        else:
            self.primary_group_combo.set_active(0)
        for cb in self.groups_checkbuttons.values():
            cb.set_active(False)
            cb.set_sensitive(True)
        self.save_btn.set_sensitive(True)
        self.username_edit.grab_focus()

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
            is_root = self._selected_user and self._selected_user.uid == 0
            if is_root:
                if password:
                    cmd = build_set_password_command(username, password)
                    success_msg = _("Password set successfully.")
                    dialog_title = _("Set Password")
                    action = CommandAction(
                        text=_("Save"),
                        running_text=_("Setting password..."),
                        dialog_title=dialog_title,
                        command=cmd,
                        success_output=success_msg,
                        parent_window=self.get_root(),
                    )
                    action.connect_finished(lambda s, e, o, u=username: self._on_action_finished(s, e, o, u))
                    action.start_action()
                    return
                else:
                    dialog = Gtk.MessageDialog(
                        transient_for=self.get_root(),
                        modal=True,
                        message_type=Gtk.MessageType.WARNING,
                        buttons=Gtk.ButtonsType.OK,
                        text=_("Error"),
                    )
                    dialog.set_property("secondary-text", _("No changes to save."))
                    dialog.connect("response", lambda d, r: d.destroy())
                    dialog.present()
                    return
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
            self.username_edit.set_editable(False)
            self._is_new_user = False
            self.user_saved.emit()