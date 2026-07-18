"""Group list widget for GTK4."""

from __future__ import annotations

import grp

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject

from mast.core.i18n import _
from mast.core.users import (
    build_delete_group_command,
    is_system_group,
)
from mast.gtk4.command.action import CommandAction


class GroupList(Gtk.Box):
    __gtype_name__ = "GroupList"
    group_selected = GObject.Signal("group-selected", arg_types=(object,))
    group_added = GObject.Signal("group-added")
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._groups: list[grp.struct_group] = []
        self._selected_group: grp.struct_group | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
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

        self.append(scrolled)

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

        self.append(button_box)

    def set_groups(self, groups: list[grp.struct_group]) -> None:
        self._groups = groups
        self._populate_group_tree()

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

    def _on_group_selected(self, selection) -> None:
        model, tree_iter = selection.get_selected()
        if tree_iter:
            self._selected_group = model.get_value(tree_iter, 1)
            if self._selected_group:
                is_system = is_system_group(self._selected_group)
                self.delete_btn.set_sensitive(not is_system)
            else:
                self.delete_btn.set_sensitive(False)
            self.group_selected.emit(self._selected_group)
        else:
            self._selected_group = None
            self.delete_btn.set_sensitive(False)
            self.group_selected.emit(None)

    def _on_add_group(self, _button) -> None:
        self.group_tree.get_selection().unselect_all()
        self._selected_group = None
        self.delete_btn.set_sensitive(False)
        self.group_added.emit()

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
            action.connect_finished(self._on_delete_finished)
            action.start_action()
        dialog.destroy()

    def _on_delete_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._selected_group = None
            self.delete_btn.set_sensitive(False)