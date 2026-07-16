"""Dialog components for the SSH module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.ssh import get_available_options


class SSHOptionEditDialog(Gtk.Dialog):
    """Dialog for editing SSH config options."""

    def __init__(self, parent, options: dict[str, str] = None):
        super().__init__(
            title=_("Edit SSH Options"),
            transient_for=parent,
            modal=True,
        )
        self.options = dict(options) if options else {}

        self.set_default_size(600, 400)

        # Add buttons
        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("OK"), Gtk.ResponseType.OK)

        # Content area
        content = self.get_content_area()
        content.set_spacing(8)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        # Scroll area for options
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        self.options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.set_child(self.options_box)
        content.append(scrolled)

        # Available options
        self.available_options = get_available_options()

        # Add known options
        for key, desc in self.available_options:
            self._add_option_row(key, desc, self.options.get(key, ""))

        # Add custom option section
        custom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.custom_key_entry = Gtk.Entry()
        self.custom_key_entry.set_placeholder_text(_("Option name"))
        self.custom_value_entry = Gtk.Entry()
        self.custom_value_entry.set_placeholder_text(_("Option value"))
        add_btn = Gtk.Button(label=_("Add"))
        add_btn.connect("clicked", self._on_add_custom_option)
        custom_box.append(self.custom_key_entry)
        custom_box.append(self.custom_value_entry)
        custom_box.append(add_btn)
        content.append(custom_box)

    def _add_option_row(self, key: str, desc: str, value: str) -> None:
        """Add an option row."""
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        key_label = Gtk.Label(label=key)
        key_label.set_size_request(150, -1)
        key_label.set_halign(Gtk.Align.START)
        row_box.append(key_label)

        entry = Gtk.Entry()
        entry.set_placeholder_text(desc)
        entry.set_text(value)
        entry.set_hexpand(True)
        entry.connect("changed", self._on_option_changed, key)
        row_box.append(entry)

        self.options_box.append(row_box)

    def _on_option_changed(self, entry: Gtk.Entry, key: str) -> None:
        """Update option value."""
        value = entry.get_text().strip()
        if value:
            self.options[key] = value
        elif key in self.options:
            del self.options[key]

    def _on_add_custom_option(self, button: Gtk.Button) -> None:
        """Add a custom option."""
        key = self.custom_key_entry.get_text().strip()
        value = self.custom_value_entry.get_text().strip()

        if not key:
            self._show_error(_("Option name is required."))
            return

        # Check if already exists
        exists = any(k.lower() == key.lower() for k in self.options.keys())
        if exists:
            self._show_error(_("Option already exists."))
            return

        self.options[key] = value
        self._add_option_row(key, "", value)
        self.custom_key_entry.set_text("")
        self.custom_value_entry.set_text("")

    def _show_error(self, message: str) -> None:
        """Show an error message."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=_("Error"),
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def get_options(self) -> dict[str, str]:
        """Get the current options."""
        return self.options


class SSHEditDialog(Gtk.Dialog):
    """Dialog for adding or editing an SSH host entry."""

    def __init__(self, parent, host: str = "", options: dict[str, str] = None):
        super().__init__(
            title=_("Add/Edit SSH Host"),
            transient_for=parent,
            modal=True,
        )
        self.options = dict(options) if options else {}

        self.set_default_size(500, -1)

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

        # Host pattern
        host_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        host_label = Gtk.Label(label=_("Host Pattern:"))
        host_label.set_size_request(100, -1)
        host_label.set_halign(Gtk.Align.START)
        host_box.append(host_label)
        self.host_entry = Gtk.Entry()
        self.host_entry.set_text(host)
        self.host_entry.set_hexpand(True)
        host_box.append(self.host_entry)
        content.append(host_box)

        # Options button
        self.options_btn = Gtk.Button(label=_("Edit Options"))
        self.options_btn.connect("clicked", self._on_edit_options)
        content.append(self.options_btn)

        # Options summary
        self.options_summary = Gtk.Label()
        self.options_summary.add_css_class("dim-label")
        self._update_options_summary()
        content.append(self.options_summary)

    def _on_edit_options(self, button: Gtk.Button) -> None:
        """Open options editing dialog."""
        dialog = SSHOptionEditDialog(self, self.options)
        dialog.connect("response", self._on_options_dialog_response)
        dialog.present()

    def _on_options_dialog_response(self, dialog, response_id) -> None:
        """Handle options dialog response."""
        if response_id == Gtk.ResponseType.OK:
            self.options = dialog.get_options()
            self._update_options_summary()
        dialog.destroy()

    def _update_options_summary(self) -> None:
        """Update the options summary display."""
        if self.options:
            summary = _("Options: {0}").format(", ".join(self.options.keys()))
        else:
            summary = _("No options set")
        self.options_summary.set_text(summary)

    def get_values(self) -> tuple[str, dict[str, str]]:
        """Get the host pattern and options."""
        return self.host_entry.get_text().strip(), self.options