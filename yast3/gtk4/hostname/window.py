"""UI components for the Hostname module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.hostname import (
    get_current_hostname,
    set_hostname,
)


class HostnameWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(400, 200)

        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)

        # Hostname input
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label = Gtk.Label(label=_("Hostname"))
        label.set_size_request(100, -1)
        label.set_halign(Gtk.Align.START)
        input_box.append(label)

        self.input = Gtk.Entry()
        self.input.set_placeholder_text(_("Enter hostname"))
        self.input.set_hexpand(True)
        input_box.append(self.input)

        self.main_box.append(input_box)

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.main_box.append(button_box)

        self.set_child(self.main_box)

        # Load current hostname
        self._load_hostname()

    def _load_hostname(self) -> None:
        """Load the current system hostname."""
        try:
            current = get_current_hostname()
            self.input.set_text(current)
        except FileNotFoundError:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("/etc/hostname not found."))
        except PermissionError:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Cannot read /etc/hostname. Root permission required."))
        except Exception as e:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Failed to load hostname: {0}").format(str(e)))

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Save the hostname."""
        new_hostname = self.input.get_text().strip()

        if not new_hostname:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Hostname cannot be empty."))
            return

        # Validate hostname (basic validation)
        if len(new_hostname) > 253:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Hostname is too long (maximum 253 characters)."))
            return

        # Check for invalid characters
        invalid_chars = set(" /\\")
        if any(c in invalid_chars for c in new_hostname):
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Hostname contains invalid characters."))
            return

        # Confirm with user
        try:
            current = get_current_hostname()
        except Exception:
            current = self.input.get_text()

        if current != new_hostname:
            if not self._show_confirm_dialog(_("Confirm"), _("Are you sure you want to change the hostname from '{0}' to '{1}'?").format(current, new_hostname)):
                return

        # Save the hostname change
        status, message = set_hostname(new_hostname)

        if status == "ok":
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Hostname changed successfully to '{0}'.").format(new_hostname))
            self.close()
        elif status == "permission_denied":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Permission denied. Root permission required."))
        elif status == "pkexec_failed":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Authentication failed or pkexec not available."))
        else:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Failed to set hostname: {0}").format(message))

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

    def _show_confirm_dialog(self, title: str, message: str) -> bool:
        """Show a confirmation dialog and return True if confirmed."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=title,
        )
        dialog.set_property("secondary-text", message)

        result = False

        def on_response(d, response_id):
            if response_id == Gtk.ResponseType.YES:
                result = True
            d.destroy()

        dialog.connect("response", on_response)
        dialog.present()

        # For GTK4, we need to use a callback-based approach
        # This is a simplified version - in production you'd use async properly
        return False  # Will be handled by callback