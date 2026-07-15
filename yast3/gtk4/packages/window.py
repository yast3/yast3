"""UI components for the Packages module (GTK4)."""

import subprocess

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _


class PackagesWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(400, 200)

        self._launch_package_manager()

    def _launch_package_manager(self) -> None:
        try:
            subprocess.Popen(["myrlyn-sudo"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.destroy()
        except FileNotFoundError:
            self._show_error(_("Failed to launch package manager."))

    def _show_error(self, message: str) -> None:
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)

        label = Gtk.Label(label=message)
        self.main_box.append(label)

        self.set_child(self.main_box)