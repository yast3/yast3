"""UI components for the Hosts module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.hosts import HostEntry, load_hosts, save_hosts

HOSTS_FILE = "/etc/hosts"


class HostsWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hosts_entries: list[HostEntry] = []

        self.set_default_size(800, 600)
        self.set_title(_("Hosts Configuration — YaST3"))

        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)

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

        self.main_box.append(button_box)

        # Create list view for hosts
        self._create_list_view()

        self.set_child(self.main_box)

        # Load hosts
        self._load_hosts()

    def _create_list_view(self) -> None:
        """Create the list view for hosts entries."""
        # Create list store
        self.list_store = Gtk.ListStore(str, str, str, str, bool, bool)

        # Create tree view
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        # Enabled column
        enabled_renderer = Gtk.CellRendererToggle()
        enabled_renderer.connect("toggled", self._on_enabled_toggled)
        enabled_column = Gtk.TreeViewColumn(_("Enabled"), enabled_renderer, active=4)
        enabled_column.set_resizable(True)
        enabled_column.set_min_width(60)
        self.tree_view.append_column(enabled_column)

        # IP Address column
        ip_renderer = Gtk.CellRendererText()
        ip_column = Gtk.TreeViewColumn(_("IP Address"), ip_renderer, text=1)
        ip_column.set_resizable(True)
        ip_column.set_min_width(150)
        self.tree_view.append_column(ip_column)

        # Hostname column
        hostname_renderer = Gtk.CellRendererText()
        hostname_column = Gtk.TreeViewColumn(_("Hostname"), hostname_renderer, text=2)
        hostname_column.set_resizable(True)
        hostname_column.set_min_width(200)
        self.tree_view.append_column(hostname_column)

        # Comment column
        comment_renderer = Gtk.CellRendererText()
        comment_column = Gtk.TreeViewColumn(_("Comment"), comment_renderer, text=3)
        comment_column.set_resizable(True)
        self.tree_view.append_column(comment_column)

        # Selection
        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        # Add tree view to scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.main_box.append(scrolled)

    def _load_hosts(self) -> None:
        """Load hosts from /etc/hosts file."""
        self.hosts_entries.clear()
        self.list_store.clear()

        try:
            self.hosts_entries = load_hosts()
        except PermissionError:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Cannot read {0}. Root permission required.").format(HOSTS_FILE))
            return
        except FileNotFoundError:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("{0} not found.").format(HOSTS_FILE))
            return

        self._populate_list()

    def _populate_list(self) -> None:
        """Populate the list with host entries."""
        for entry in self.hosts_entries:
            hostnames_str = " ".join(entry.hostnames)
            self.list_store.append([
                "",  # ID placeholder
                entry.ip,
                hostnames_str,
                entry.comment,
                entry.enabled,
                entry.editable,
            ])

    def _on_enabled_toggled(self, renderer, path) -> None:
        """Handle enabled toggle."""
        index = int(path)
        if 0 <= index < len(self.hosts_entries):
            entry = self.hosts_entries[index]
            if entry.editable:
                entry.enabled = not entry.enabled
                # Update the list store
                tree_iter = self.list_store.get_iter(path)
                self.list_store.set_value(tree_iter, 4, entry.enabled)

    def _on_add_clicked(self, button: Gtk.Button) -> None:
        """Add a new host entry."""
        dialog = HostsEditDialog(self)
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response_id) -> None:
        """Handle add dialog response."""
        if response_id == Gtk.ResponseType.OK:
            ip, hostname_str, comment = dialog.get_values()
            hostnames = hostname_str.split() if hostname_str else []
            if ip and hostnames:
                comment_sep = "\t# " if comment else ""
                self.hosts_entries.append(
                    HostEntry(
                        enabled=True,
                        ip=ip,
                        hostnames=hostnames,
                        comment_sep=comment_sep,
                        comment=comment,
                        editable=True,
                    )
                )
                self._populate_list()
            else:
                self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("IP address and hostname are required."))
        dialog.destroy()

    def _on_edit_clicked(self, button: Gtk.Button) -> None:
        """Edit the selected host entry."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a host entry to edit."))
            return

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        entry = self.hosts_entries[index]

        dialog = HostsEditDialog(self, entry.ip, " ".join(entry.hostnames), entry.comment)
        dialog.connect("response", self._on_edit_dialog_response, index)
        dialog.present()

    def _on_edit_dialog_response(self, dialog, response_id, index: int) -> None:
        """Handle edit dialog response."""
        if response_id == Gtk.ResponseType.OK:
            new_ip, new_hostname_str, new_comment = dialog.get_values()
            new_hostnames = new_hostname_str.split() if new_hostname_str else []
            if new_ip and new_hostnames:
                entry = self.hosts_entries[index]
                new_comment_sep = entry.comment_sep if entry.comment_sep else ("\t# " if new_comment else "")
                self.hosts_entries[index] = HostEntry(
                    enabled=entry.enabled,
                    ip=new_ip,
                    hostnames=new_hostnames,
                    comment_sep=new_comment_sep,
                    comment=new_comment,
                    editable=entry.editable,
                )
                self._populate_list()
            else:
                self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("IP address and hostname are required."))
        dialog.destroy()

    def _on_delete_clicked(self, button: Gtk.Button) -> None:
        """Delete the selected host entry."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a host entry to delete."))
            return

        # Show confirmation dialog
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self,
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
            self.hosts_entries.pop(index)
            self.list_store.remove(tree_iter)
        dialog.destroy()

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Save hosts to /etc/hosts file."""
        result = save_hosts(self.hosts_entries)

        if result == "ok":
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Hosts file saved successfully."))
        elif result == "permission_denied":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Cannot write to {0}. Root permission required.").format(HOSTS_FILE))
        elif result == "pkexec_failed":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Authentication failed or pkexec not available."))
        else:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Failed to save hosts file."))

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        """Show a message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


class HostsEditDialog(Gtk.Dialog):
    """Dialog for adding or editing a host entry."""

    def __init__(self, parent, ip: str = "", hostname: str = "", comment: str = ""):
        super().__init__(
            title=_("Add/Edit Host Entry"),
            transient_for=parent,
            modal=True,
        )
        self.set_default_size(400, -1)

        # Add buttons
        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("OK"), Gtk.ResponseType.OK)

        # Content area
        content = self.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        # IP address
        ip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        ip_label = Gtk.Label(label=_("IP Address:"))
        ip_label.set_size_request(100, -1)
        ip_label.set_halign(Gtk.Align.START)
        ip_box.append(ip_label)
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_text(ip)
        self.ip_entry.set_hexpand(True)
        ip_box.append(self.ip_entry)
        content.append(ip_box)

        # Hostname
        hostname_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hostname_label = Gtk.Label(label=_("Hostname:"))
        hostname_label.set_size_request(100, -1)
        hostname_label.set_halign(Gtk.Align.START)
        hostname_box.append(hostname_label)
        self.hostname_entry = Gtk.Entry()
        self.hostname_entry.set_text(hostname)
        self.hostname_entry.set_hexpand(True)
        hostname_box.append(self.hostname_entry)
        content.append(hostname_box)

        # Comment
        comment_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        comment_label = Gtk.Label(label=_("Comment:"))
        comment_label.set_size_request(100, -1)
        comment_label.set_halign(Gtk.Align.START)
        comment_box.append(comment_label)
        self.comment_entry = Gtk.Entry()
        self.comment_entry.set_text(comment)
        self.comment_entry.set_hexpand(True)
        comment_box.append(self.comment_entry)
        content.append(comment_box)

    def get_values(self) -> tuple[str, str, str]:
        """Get the dialog values."""
        return (
            self.ip_entry.get_text().strip(),
            self.hostname_entry.get_text().strip(),
            self.comment_entry.get_text().strip(),
        )