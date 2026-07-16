"""Generate key dialog for the SSH module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.ssh.keys_manager import KeyManager


class GenerateKeyDialog(Gtk.Dialog):
    """Dialog for generating a new SSH key."""

    def __init__(self, parent):
        super().__init__(
            title=_("Generate SSH Key"),
            transient_for=parent,
            modal=True,
        )

        self.set_default_size(400, -1)

        # Add buttons
        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("Generate"), Gtk.ResponseType.OK)

        # Content area
        content = self.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        # Algorithm
        algo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        algo_label = Gtk.Label(label=_("Algorithm"))
        algo_label.set_size_request(100, -1)
        algo_label.set_halign(Gtk.Align.START)
        algo_box.append(algo_label)
        self.algo_combo = Gtk.ComboBoxText()
        for algo in ["ed25519", "rsa", "ecdsa", "dsa"]:
            self.algo_combo.append_text(algo)
        self.algo_combo.set_active(0)  # ed25519 is default
        algo_box.append(self.algo_combo)
        content.append(algo_box)

        # Key size (for RSA/ECDSA)
        size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        size_label = Gtk.Label(label=_("Key Size"))
        size_label.set_size_request(100, -1)
        size_label.set_halign(Gtk.Align.START)
        size_box.append(size_label)
        self.size_combo = Gtk.ComboBoxText()
        for size in ["2048", "3072", "4096"]:
            self.size_combo.append_text(size)
        self.size_combo.set_active(0)
        size_box.append(self.size_combo)
        content.append(size_box)

        # Comment
        comment_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        comment_label = Gtk.Label(label=_("Comment"))
        comment_label.set_size_request(100, -1)
        comment_label.set_halign(Gtk.Align.START)
        comment_box.append(comment_label)
        self.comment_entry = Gtk.Entry()
        self.comment_entry.set_placeholder_text(_("Optional comment (e.g., user@host)"))
        self.comment_entry.set_hexpand(True)
        comment_box.append(self.comment_entry)
        content.append(comment_box)

        # Passphrase
        passphrase_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        passphrase_label = Gtk.Label(label=_("Passphrase"))
        passphrase_label.set_size_request(100, -1)
        passphrase_label.set_halign(Gtk.Align.START)
        passphrase_box.append(passphrase_label)
        self.passphrase_entry = Gtk.Entry()
        self.passphrase_entry.set_placeholder_text(_("Optional passphrase"))
        self.passphrase_entry.set_visibility(False)
        self.passphrase_entry.set_hexpand(True)
        passphrase_box.append(self.passphrase_entry)
        content.append(passphrase_box)

        # Connect OK button to generate
        ok_btn = self.get_widget_for_response(Gtk.ResponseType.OK)
        if ok_btn:
            ok_btn.connect("clicked", self._on_generate_clicked)

    def _on_generate_clicked(self, button: Gtk.Button) -> None:
        """Generate the SSH key."""
        algo = self.algo_combo.get_active_text()
        size = self.size_combo.get_active_text()
        comment = self.comment_entry.get_text().strip()
        passphrase = self.passphrase_entry.get_text()

        success, error = KeyManager.generate_key(algo, size, comment, passphrase)

        if success:
            self.response(Gtk.ResponseType.OK)
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error"),
            )
            dialog.set_property("secondary-text", _("Failed to generate key: {0}").format(error))
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()