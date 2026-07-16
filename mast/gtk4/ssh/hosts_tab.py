"""Hosts tab UI component for the SSH module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.ssh import SSHConfigEntry
from mast.gtk4.ssh.dialogs import SSHEditDialog
from mast.gtk4.ssh.hosts_manager import HostManager


class HostsTab(Gtk.Box):
    """Hosts tab for managing SSH config entries."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.entries: list[SSHConfigEntry] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

        # Button bar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.add_btn = Gtk.Button(label=_("Add"))
        self.add_btn.connect("clicked", self._on_add_clicked)
        button_box.append(self.add_btn)

        self.edit_btn = Gtk.Button(label=_("Edit"))
        self.edit_btn.connect("clicked", self._on_edit_clicked)
        button_box.append(self.edit_btn)

        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.connect("clicked", self._on_delete_clicked)
        button_box.append(self.delete_btn)

        button_box.append(Gtk.Box())  # Spacer
        button_box.set_hexpand(True)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.append(button_box)

        # Create list view
        self._create_list_view()

        # Load config
        self._load_config()

    def _create_list_view(self) -> None:
        """Create the list view for SSH config entries."""
        # Create list store
        self.list_store = Gtk.ListStore(bool, str, str)

        # Create tree view
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        # Enabled column
        enabled_renderer = Gtk.CellRendererToggle()
        enabled_renderer.connect("toggled", self._on_enabled_toggled)
        enabled_column = Gtk.TreeViewColumn(_("Enabled"), enabled_renderer, active=0)
        enabled_column.set_resizable(True)
        enabled_column.set_min_width(60)
        self.tree_view.append_column(enabled_column)

        # Host pattern column
        host_renderer = Gtk.CellRendererText()
        host_column = Gtk.TreeViewColumn(_("Host Pattern"), host_renderer, text=1)
        host_column.set_resizable(True)
        host_column.set_min_width(200)
        self.tree_view.append_column(host_column)

        # Options column
        options_renderer = Gtk.CellRendererText()
        options_column = Gtk.TreeViewColumn(_("Options"), options_renderer, text=2)
        options_column.set_resizable(True)
        self.tree_view.append_column(options_column)

        # Selection
        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        # Add tree view to scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.append(scrolled)

    def _load_config(self) -> None:
        """Load SSH config from ~/.ssh/config file."""
        self.entries.clear()
        self.list_store.clear()

        entries, error = HostManager.load_config()
        if error:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _(error))
            return

        self.entries = entries
        self._populate_list()

    def _populate_list(self) -> None:
        """Populate the list with SSH config entries."""
        for entry in self.entries:
            # Options (show first 3 option names)
            option_names = list(entry.options.keys())[:3]
            options_text = ", ".join(option_names)
            if len(entry.options) > 3:
                options_text += _(" and {0} more").format(len(entry.options) - 3)
            self.list_store.append([
                entry.enabled,
                entry.host,
                options_text,
            ])

    def _on_enabled_toggled(self, renderer, path) -> None:
        """Handle enabled toggle."""
        index = int(path)
        if 0 <= index < len(self.entries):
            self.entries[index].enabled = not self.entries[index].enabled
            # Update the list store
            tree_iter = self.list_store.get_iter(path)
            self.list_store.set_value(tree_iter, 0, self.entries[index].enabled)

    def _on_add_clicked(self, button: Gtk.Button) -> None:
        """Add a new SSH host entry."""
        dialog = SSHEditDialog(self.get_root())
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response_id) -> None:
        """Handle add dialog response."""
        if response_id == Gtk.ResponseType.OK:
            host, options = dialog.get_values()
            if host:
                self.entries.append(HostManager.create_entry(host, options))
                self._populate_list()
            else:
                self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Host pattern is required."))
        dialog.destroy()

    def _on_edit_clicked(self, button: Gtk.Button) -> None:
        """Edit the selected SSH host entry."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a host entry to edit."))
            return

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        entry = self.entries[index]

        dialog = SSHEditDialog(self.get_root(), entry.host, entry.options)
        dialog.connect("response", self._on_edit_dialog_response, index)
        dialog.present()

    def _on_edit_dialog_response(self, dialog, response_id, index: int) -> None:
        """Handle edit dialog response."""
        if response_id == Gtk.ResponseType.OK:
            new_host, new_options = dialog.get_values()
            if new_host:
                self.entries[index] = HostManager.update_entry(
                    self.entries[index], new_host, new_options
                )
                self._populate_list()
            else:
                self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Host pattern is required."))
        dialog.destroy()

    def _on_delete_clicked(self, button: Gtk.Button) -> None:
        """Delete the selected SSH host entry."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a host entry to delete."))
            return

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        entry = self.entries[index]

        if not HostManager.can_delete(entry):
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Cannot delete the default host entry."))
            return

        # Show confirmation dialog
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.set_property("secondary-text", _("Are you sure you want to delete this entry?"))
        confirm_dialog.connect("response", self._on_delete_confirm_response, tree_iter)
        confirm_dialog.present()

    def _on_delete_confirm_response(self, dialog, response_id, tree_iter) -> None:
        """Handle delete confirmation response."""
        if response_id == Gtk.ResponseType.YES:
            path = self.list_store.get_path(tree_iter)
            index = int(path.to_string())
            self.entries.pop(index)
            self.list_store.remove(tree_iter)
        dialog.destroy()

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Save SSH config to ~/.ssh/config file."""
        result = HostManager.save_config(self.entries)

        if result == "ok":
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("SSH config saved successfully."))
        elif result == "permission_denied":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Cannot write to SSH config. Check permissions."))
        else:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Failed to save SSH config."))

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        """Show a message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()