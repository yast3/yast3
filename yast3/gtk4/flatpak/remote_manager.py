"""GTK4 Flatpak remote management widget."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.flatpak import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
)
from yast3.core.i18n import _


class FlatpakRemoteManager(Gtk.Box):
    """Table-style Flatpak remote management component."""

    def __init__(self, parent_window: Gtk.ApplicationWindow, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.parent_window = parent_window
        self.remotes: list[FlatpakRemote] = []

        button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.add_btn = Gtk.Button(label=_("Add"))
        self.add_btn.connect("clicked", self._on_add_clicked)
        button_bar.append(self.add_btn)

        self.edit_btn = Gtk.Button(label=_("Edit"))
        self.edit_btn.connect("clicked", self._on_edit_clicked)
        button_bar.append(self.edit_btn)

        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.connect("clicked", self._on_delete_clicked)
        button_bar.append(self.delete_btn)

        self.refresh_btn = Gtk.Button(label=_("Refresh"))
        self.refresh_btn.connect("clicked", self._on_refresh_clicked)
        button_bar.append(self.refresh_btn)

        button_bar.append(Gtk.Box(hexpand=True))
        self.append(button_bar)

        self.list_store = Gtk.ListStore(str, str, str)
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        self._append_column(_("Name"), 0, min_width=180)
        self._append_column(_("URL"), 1)
        self._append_column(_("Scope"), 2, min_width=90)

        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.append(scrolled)

        self.load_remotes()

    def _append_column(self, title: str, index: int, min_width: int = 0) -> None:
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=index)
        column.set_resizable(True)
        if min_width > 0:
            column.set_min_width(min_width)
        self.tree_view.append_column(column)

    def load_remotes(self) -> None:
        try:
            self.remotes = list_flatpak_remotes()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to load Flatpak remotes: {0}").format(str(e)),
            )
            self.remotes = []

        self.list_store.clear()
        for remote in self.remotes:
            self.list_store.append([remote.name, remote.url, remote.scope])

    def _selected_remote(self) -> FlatpakRemote | None:
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            return None

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        if 0 <= index < len(self.remotes):
            return self.remotes[index]
        return None

    def _on_refresh_clicked(self, _button: Gtk.Button) -> None:
        self.load_remotes()

    def _on_add_clicked(self, _button: Gtk.Button) -> None:
        self._show_add_dialog()

    def _on_edit_clicked(self, _button: Gtk.Button) -> None:
        remote = self._selected_remote()
        if remote is None:
            self._show_message_dialog(
                Gtk.MessageType.INFO,
                _("Information"),
                _("Please select a remote to edit."),
            )
            return
        self._show_edit_dialog(remote)

    def _on_delete_clicked(self, _button: Gtk.Button) -> None:
        remote = self._selected_remote()
        if remote is None:
            self._show_message_dialog(
                Gtk.MessageType.INFO,
                _("Information"),
                _("Please select a remote to delete."),
            )
            return

        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        dialog.set_property(
            "secondary-text",
            _("Are you sure you want to delete remote '{0}'?").format(remote.name),
        )
        dialog.connect("response", self._on_delete_confirm, remote)
        dialog.present()

    def _on_delete_confirm(
        self,
        dialog: Gtk.MessageDialog,
        response_id: Gtk.ResponseType,
        remote: FlatpakRemote,
    ) -> None:
        dialog.destroy()
        if response_id != Gtk.ResponseType.YES:
            return

        try:
            delete_flatpak_remote(remote.name, remote.scope)
            self._show_message_dialog(
                Gtk.MessageType.INFO,
                _("Success"),
                _("Remote deleted successfully."),
            )
            self.load_remotes()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to delete remote: {0}").format(str(e)),
            )

    def _show_add_dialog(self) -> None:
        dialog = Gtk.Dialog(
            title=_("Add Remote"),
            transient_for=self.parent_window,
            modal=True,
        )
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("OK"), Gtk.ResponseType.OK)

        content = dialog.get_content_area()
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(8)

        name_entry = Gtk.Entry()
        url_entry = Gtk.Entry()
        scope_combo = Gtk.ComboBoxText()
        scope_combo.append("system", _("System"))
        scope_combo.append("user", _("User"))
        scope_combo.set_active_id("system")

        grid.attach(Gtk.Label(label=_("Name")), 0, 0, 1, 1)
        grid.attach(name_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=_("URL")), 0, 1, 1, 1)
        grid.attach(url_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label=_("Scope")), 0, 2, 1, 1)
        grid.attach(scope_combo, 1, 2, 1, 1)

        content.append(grid)
        dialog.connect("response", self._on_add_dialog_response, name_entry, url_entry, scope_combo)
        dialog.present()

    def _on_add_dialog_response(
        self,
        dialog: Gtk.Dialog,
        response_id: Gtk.ResponseType,
        name_entry: Gtk.Entry,
        url_entry: Gtk.Entry,
        scope_combo: Gtk.ComboBoxText,
    ) -> None:
        if response_id == Gtk.ResponseType.OK:
            name = name_entry.get_text().strip()
            url = url_entry.get_text().strip()
            scope = scope_combo.get_active_id() or "system"
            try:
                add_flatpak_remote(name, url, scope)
                self._show_message_dialog(
                    Gtk.MessageType.INFO,
                    _("Success"),
                    _("Remote added successfully."),
                )
                self.load_remotes()
            except Exception as e:
                self._show_message_dialog(
                    Gtk.MessageType.ERROR,
                    _("Error"),
                    _("Failed to add remote: {0}").format(str(e)),
                )
        dialog.destroy()

    def _show_edit_dialog(self, remote: FlatpakRemote) -> None:
        dialog = Gtk.Dialog(
            title=_("Edit"),
            transient_for=self.parent_window,
            modal=True,
        )
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("OK"), Gtk.ResponseType.OK)

        content = dialog.get_content_area()
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(8)

        name_label = Gtk.Label(label=remote.name)
        name_label.set_halign(Gtk.Align.START)
        url_entry = Gtk.Entry()
        url_entry.set_text(remote.url)
        scope_label = Gtk.Label(label=remote.scope)
        scope_label.set_halign(Gtk.Align.START)

        grid.attach(Gtk.Label(label=_("Name")), 0, 0, 1, 1)
        grid.attach(name_label, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=_("URL")), 0, 1, 1, 1)
        grid.attach(url_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label=_("Scope")), 0, 2, 1, 1)
        grid.attach(scope_label, 1, 2, 1, 1)

        content.append(grid)
        dialog.connect("response", self._on_edit_dialog_response, remote, url_entry)
        dialog.present()

    def _on_edit_dialog_response(
        self,
        dialog: Gtk.Dialog,
        response_id: Gtk.ResponseType,
        remote: FlatpakRemote,
        url_entry: Gtk.Entry,
    ) -> None:
        if response_id == Gtk.ResponseType.OK:
            url = url_entry.get_text().strip()
            try:
                modify_flatpak_remote_url(remote.name, url, remote.scope)
                self._show_message_dialog(
                    Gtk.MessageType.INFO,
                    _("Success"),
                    _("Remote URL updated successfully."),
                )
                self.load_remotes()
            except Exception as e:
                self._show_message_dialog(
                    Gtk.MessageType.ERROR,
                    _("Error"),
                    _("Failed to update remote URL: {0}").format(str(e)),
                )
        dialog.destroy()

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
