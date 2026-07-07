"""UI components for the Flatpak module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.flatpak import (
    install_flatpak_pkexec,
    is_flatpak_installed,
    remove_flatpak_pkexec,
)
from yast3.core.i18n import _
from yast3.gtk4.flatpak.remote_manager import FlatpakRemoteManager


class FlatpakWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(760, 520)
        self.set_title(_("{} — YaST3").format(_("Flatpak")))

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)

        self.install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        install_title = Gtk.Label(label=_("Flatpak is not installed"))
        install_title.set_halign(Gtk.Align.START)
        self.install_btn = Gtk.Button(label=_("Install Flatpak"))
        self.install_btn.add_css_class("suggested-action")
        self.install_btn.connect("clicked", self._on_install_clicked)
        self.install_box.append(install_title)
        self.install_box.append(self.install_btn)
        self.main_box.append(self.install_box)

        self.manage_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.remote_manager = FlatpakRemoteManager(self)
        self.manage_box.append(self.remote_manager)

        remove_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        remove_box.set_halign(Gtk.Align.END)
        self.remove_flatpak_btn = Gtk.Button(label=_("Remove Flatpak"))
        self.remove_flatpak_btn.connect("clicked", self._on_remove_flatpak_clicked)
        remove_box.append(self.remove_flatpak_btn)
        self.manage_box.append(remove_box)

        self.main_box.append(self.manage_box)
        self.set_child(self.main_box)

        self._refresh_state()

    def _refresh_state(self) -> None:
        installed = is_flatpak_installed()
        if installed:
            self.install_box.set_visible(False)
            self.manage_box.set_visible(True)
            self.remote_manager.load_remotes()
        else:
            self.manage_box.set_visible(False)
            self.install_box.set_visible(True)

    def _on_install_clicked(self, _button: Gtk.Button) -> None:
        try:
            install_flatpak_pkexec()
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Flatpak installed successfully."))
            self._refresh_state()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to install Flatpak: {0}").format(str(e)),
            )

    def _on_remove_flatpak_clicked(self, _button: Gtk.Button) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        dialog.set_property("secondary-text", _("Are you sure you want to remove Flatpak?"))
        dialog.connect("response", self._on_remove_flatpak_confirm)
        dialog.present()

    def _on_remove_flatpak_confirm(self, dialog: Gtk.MessageDialog, response_id: Gtk.ResponseType) -> None:
        dialog.destroy()
        if response_id != Gtk.ResponseType.YES:
            return

        try:
            remove_flatpak_pkexec()
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Flatpak removed successfully."))
            self._refresh_state()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to remove Flatpak: {0}").format(str(e)),
            )

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
