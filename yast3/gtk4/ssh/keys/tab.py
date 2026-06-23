"""Keys tab UI component for the SSH module (GTK4)."""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.gtk4.ssh.keys.generate_dialog import GenerateKeyDialog
from yast3.gtk4.ssh.keys.manager import KeyInfo, KeyManager


class KeysTab(Gtk.Box):
    """Keys tab for displaying SSH key files."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.key_list: list[KeyInfo] = []
        self._setup_ui()
        self._load_keys()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

        # Button bar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.new_key_btn = Gtk.Button(label=_("Add"))
        self.new_key_btn.connect("clicked", self._on_generate_new_key)
        button_box.append(self.new_key_btn)

        self.copy_key_btn = Gtk.Button(label=_("Copy Public Key"))
        self.copy_key_btn.connect("clicked", self._on_copy_key)
        self.copy_key_btn.set_sensitive(False)
        button_box.append(self.copy_key_btn)

        self.delete_key_btn = Gtk.Button(label=_("Delete"))
        self.delete_key_btn.connect("clicked", self._on_delete_key)
        self.delete_key_btn.set_sensitive(False)
        button_box.append(self.delete_key_btn)

        self.refresh_btn = Gtk.Button(label=_("Refresh"))
        self.refresh_btn.connect("clicked", self._on_refresh)
        button_box.append(self.refresh_btn)

        self.pack_start(button_box, True, True, 0)

        # Create list view
        self._create_list_view()

    def _create_list_view(self) -> None:
        """Create the list view for SSH keys."""
        # Create list store
        self.list_store = Gtk.ListStore(str, str, str, str, str, str, str, str)

        # Create tree view
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        # Name column
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn(_("Name"), name_renderer, text=0)
        name_column.set_resizable(True)
        name_column.set_min_width(160)
        self.tree_view.append_column(name_column)

        # Algorithm column
        algorithm_renderer = Gtk.CellRendererText()
        algorithm_column = Gtk.TreeViewColumn(_("Algorithm"), algorithm_renderer, text=1)
        algorithm_column.set_resizable(True)
        algorithm_column.set_min_width(90)
        self.tree_view.append_column(algorithm_column)

        # Size column
        size_renderer = Gtk.CellRendererText()
        size_column = Gtk.TreeViewColumn(_("Size"), size_renderer, text=2)
        size_column.set_resizable(True)
        size_column.set_min_width(60)
        self.tree_view.append_column(size_column)

        # Fingerprint column
        fingerprint_renderer = Gtk.CellRendererText()
        fingerprint_column = Gtk.TreeViewColumn(_("Fingerprint"), fingerprint_renderer, text=3)
        fingerprint_column.set_resizable(True)
        fingerprint_column.set_min_width(220)
        self.tree_view.append_column(fingerprint_column)

        # Comment column
        comment_renderer = Gtk.CellRendererText()
        comment_column = Gtk.TreeViewColumn(_("Comment"), comment_renderer, text=4)
        comment_column.set_resizable(True)
        self.tree_view.append_column(comment_column)

        # Passphrase column
        passphrase_renderer = Gtk.CellRendererText()
        passphrase_column = Gtk.TreeViewColumn(_("Passphrase"), passphrase_renderer, text=5)
        passphrase_column.set_resizable(True)
        passphrase_column.set_min_width(80)
        self.tree_view.append_column(passphrase_column)

        # Public column
        public_renderer = Gtk.CellRendererText()
        public_column = Gtk.TreeViewColumn(_("Public"), public_renderer, text=6)
        public_column.set_resizable(True)
        public_column.set_min_width(70)
        self.tree_view.append_column(public_column)

        # Private column
        private_renderer = Gtk.CellRendererText()
        private_column = Gtk.TreeViewColumn(_("Private"), private_renderer, text=7)
        private_column.set_resizable(True)
        private_column.set_min_width(70)
        self.tree_view.append_column(private_column)

        # Selection
        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self._on_selection_changed)

        # Add tree view to scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.pack_start(scrolled, True, True, 0)

    def _load_keys(self) -> None:
        """Load SSH keys from ~/.ssh/ directory."""
        self.list_store.clear()

        # Use KeyManager to get key list
        self.key_list = KeyManager.list_keys()

        # Populate table
        for key_info in self.key_list:
            self.list_store.append([
                key_info.name,
                key_info.algorithm,
                key_info.size,
                key_info.fingerprint or "-",
                key_info.comment or "-",
                _("Yes") if key_info.has_passphrase else _("No"),
                _("Yes") if key_info.has_public else _("No"),
                _("Yes") if key_info.has_private else _("No"),
            ])

    def _on_selection_changed(self, selection) -> None:
        """Handle table selection change."""
        model, tree_iter = selection.get_selected()
        if tree_iter is not None:
            path = model.get_path(tree_iter)
            index = int(path.to_string())
            if 0 <= index < len(self.key_list):
                key_info = self.key_list[index]
                self.copy_key_btn.set_sensitive(key_info.has_public)
                self.delete_key_btn.set_sensitive(True)
                return

        self.copy_key_btn.set_sensitive(False)
        self.delete_key_btn.set_sensitive(False)

    def _on_generate_new_key(self, button: Gtk.Button) -> None:
        """Open dialog to generate a new SSH key."""
        dialog = GenerateKeyDialog(self.get_root())
        dialog.connect("response", self._on_generate_dialog_response)
        dialog.show_all()

    def _on_generate_dialog_response(self, dialog, response_id) -> None:
        """Handle generate dialog response."""
        if response_id == Gtk.ResponseType.OK:
            self._load_keys()
        dialog.destroy()

    def _on_copy_key(self, button: Gtk.Button) -> None:
        """Copy the public key of the selected key."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            return

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        if 0 <= index < len(self.key_list):
            key_info = self.key_list[index]
            content = KeyManager.get_public_key(key_info)
            if content:
                # Get clipboard
                clipboard = self.get_display().get_clipboard()
                clipboard.set_text(content)
                self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Public key copied to clipboard."))
            else:
                self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Cannot read public key file."))

    def _on_delete_key(self, button: Gtk.Button) -> None:
        """Delete the selected key pair."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            return

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        if not (0 <= index < len(self.key_list)):
            return

        key_info = self.key_list[index]

        # Build message with what will be deleted
        files_to_delete = []
        if key_info.has_private:
            files_to_delete.append(key_info.name)
        if key_info.has_public:
            files_to_delete.append(key_info.name + ".pub")

        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm Delete"),
        )
        confirm_dialog.format_secondary_text(
            _("Are you sure you want to delete the following keys?\n\n{0}").format(
                "\n".join(files_to_delete)
            )
        )
        confirm_dialog.connect("response", self._on_delete_confirm_response, index)
        confirm_dialog.show_all()

    def _on_delete_confirm_response(self, dialog, response_id, index: int) -> None:
        """Handle delete confirmation response."""
        if response_id == Gtk.ResponseType.YES:
            key_info = self.key_list[index]
            success, errors = KeyManager.delete_key(key_info)

            if errors:
                self._show_message_dialog(
                    Gtk.MessageType.WARNING,
                    _("Error"),
                    _("Failed to delete some files:\n\n{0}").format("\n".join(errors))
                )
            else:
                self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Key deleted successfully."))
                self._load_keys()
        dialog.destroy()

    def _on_refresh(self, button: Gtk.Button) -> None:
        """Refresh the key list."""
        self._load_keys()

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        """Show a message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show_all()