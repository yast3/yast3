"""UI components for the SSH module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.gtk4.ssh.hosts import HostsTab
from yast3.gtk4.ssh.keys import KeysTab


class SSHWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(960, 640)

        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)

        # Notebook for tabs
        self.notebook = Gtk.Notebook()

        # Hosts tab
        self.hosts_tab = HostsTab()
        self.notebook.append_page(self.hosts_tab, Gtk.Label(label=_("Hosts")))

        # Keys tab
        self.keys_tab = KeysTab()
        self.notebook.append_page(self.keys_tab, Gtk.Label(label=_("Keys")))

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)