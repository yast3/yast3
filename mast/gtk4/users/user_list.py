"""User list widget for GTK4."""

from __future__ import annotations

import os

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject

from mast.core.i18n import _
from mast.core.users import UserEntry, is_user_deletable, build_delete_user_command
from mast.gtk4.command.action import CommandAction


class UserList(Gtk.Box):
    __gtype_name__ = "UserList"
    user_selected = GObject.Signal("user-selected", arg_types=(object,))
    user_added = GObject.Signal("user-added")
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._users: list[UserEntry] = []
        self._selected_user: UserEntry | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.user_list = Gtk.ListBox()
        self.user_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.user_list.connect("row-selected", self._on_user_selected)
        self.user_list.set_margin_start(8)
        self.user_list.set_margin_top(8)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.user_list)
        scrolled.set_vexpand(True)

        self.append(scrolled)

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

        self.append(button_box)

    def set_users(self, users: list[UserEntry]) -> None:
        self._users = users
        self._populate_user_list()

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

    def _on_user_selected(self, _listbox, row: Gtk.ListBoxRow | None) -> None:
        if row:
            self._selected_user = getattr(row, "user_data", None)
            if self._selected_user:
                self.delete_btn.set_sensitive(is_user_deletable(self._selected_user))
                if hasattr(self, 'user_selected'):
                    self.user_selected.emit(self._selected_user)
            else:
                self.delete_btn.set_sensitive(False)
        else:
            self._selected_user = None
            self.delete_btn.set_sensitive(False)
            if hasattr(self, 'user_selected'):
                self.user_selected.emit(None)

    def _on_add_user(self, _button) -> None:
        self.user_list.unselect_all()
        self._selected_user = None
        self.delete_btn.set_sensitive(False)
        if hasattr(self, 'user_added'):
            self.user_added.emit()

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
            action.connect_finished(self._on_delete_finished)
            action.start_action()
        dialog.destroy()

    def _on_delete_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._selected_user = None
            self.delete_btn.set_sensitive(False)

    def select_user(self, username: str) -> None:
        for row in self.user_list:
            if getattr(row, "user_data", None) and row.user_data.username == username:
                self.user_list.select_row(row)
                break