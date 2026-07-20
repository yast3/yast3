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
    user_deleted = GObject.Signal("user-deleted")

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._users: list[UserEntry] = []
        self._selected_user: UserEntry | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.user_tree = Gtk.TreeView()
        self.user_tree.set_headers_visible(False)
        self.user_tree.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.user_tree.set_margin_start(8)
        self.user_tree.set_margin_top(8)

        column = Gtk.TreeViewColumn()
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "text", 0)
        self.user_tree.append_column(column)

        self.user_store = Gtk.TreeStore(str, object)

        self.user_tree.set_model(self.user_store)
        self.user_tree.get_selection().connect("changed", self._on_user_selected)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.user_tree)
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
        self._populate_user_tree()

    def _populate_user_tree(self) -> None:
        self.user_store.clear()

        system_users_item = self.user_store.append(None, [_("System Users"), None])
        local_users_item = self.user_store.append(None, [_("Local Users"), None])

        current_username = None
        try:
            current_username = os.getlogin()
        except Exception:
            pass

        selected_iter = None
        for user in self._users:
            if user.uid == 0:
                tree_iter = self.user_store.prepend(system_users_item, [user.username, user])
            elif user.uid >= 1000:
                tree_iter = self.user_store.append(local_users_item, [user.username, user])
            else:
                tree_iter = self.user_store.append(system_users_item, [user.username, user])

            if current_username and user.username == current_username:
                selected_iter = tree_iter

        self.user_tree.expand_all()

        if selected_iter:
            selection = self.user_tree.get_selection()
            selection.select_iter(selected_iter)

    def _on_user_selected(self, selection) -> None:
        model, tree_iter = selection.get_selected()
        if tree_iter:
            self._selected_user = model.get_value(tree_iter, 1)
            if self._selected_user:
                self.delete_btn.set_sensitive(is_user_deletable(self._selected_user))
                self.user_selected.emit(self._selected_user)
            else:
                self.delete_btn.set_sensitive(False)
        else:
            self._selected_user = None
            self.delete_btn.set_sensitive(False)
            self.user_selected.emit(None)

    def _on_add_user(self, _button) -> None:
        self.user_tree.get_selection().unselect_all()
        self._selected_user = None
        self.delete_btn.set_sensitive(False)
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
            self.user_deleted.emit()

    def select_user(self, username: str) -> None:
        def find_user(model, tree_iter):
            while tree_iter:
                if model[tree_iter][0] == username:
                    selection = self.user_tree.get_selection()
                    selection.select_iter(tree_iter)
                    return True
                if model.iter_has_child(tree_iter):
                    child_iter = model.iter_children(tree_iter)
                    if find_user(model, child_iter):
                        return True
                tree_iter = model.iter_next(tree_iter)
            return False

        find_user(self.user_store, self.user_store.get_iter_first())