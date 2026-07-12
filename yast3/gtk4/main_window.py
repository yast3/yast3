"""Main application window showing module buttons."""

import webbrowser

from gi.repository import Gdk, Gtk

from yast3.core import GITHUB_URL, __version__
from yast3.gtk4 import (
    CronModule,
    DateTimeModule,
    FlatpakModule,
    GitModule,
    HostnameModule,
    HostsModule,
    LanguagesModule,
    ProxyModule,
    RepositoriesModule,
    ServicesModule,
    SnapshotsModule,
    SSHClientModule,
)
from yast3.gtk4.module_button import ModuleButton


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.modules = (
            CronModule(),
            DateTimeModule(),
            FlatpakModule(),
            GitModule(),
            HostnameModule(),
            HostsModule(),
            LanguagesModule(),
            ProxyModule(),
            RepositoriesModule(),
            ServicesModule(),
            SnapshotsModule(),
            SSHClientModule(),
        )

        self.windows = {}  # Keep track of open module windows

        self.set_title("YaST3")
        self.set_default_size(960, 640)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Create main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled.set_child(self.main_box)

        # Create grid for module buttons
        self.grid = Gtk.Grid()
        self.grid.set_margin_top(32)
        self.grid.set_margin_bottom(32)
        self.grid.set_margin_start(32)
        self.grid.set_margin_end(32)
        self.grid.set_row_spacing(24)
        self.grid.set_column_spacing(24)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.START)

        # Add module buttons
        for index, module in enumerate(self.modules):
            button = ModuleButton(module, self)
            row, column = divmod(index, 4)
            self.grid.attach(button, column, row, 1, 1)

        self.main_box.append(self.grid)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        footer.set_margin_start(16)
        footer.set_margin_end(16)
        footer.set_margin_bottom(8)
        footer.set_spacing(12)

        version_label = Gtk.Label(label=f"v{__version__}")
        version_label.set_xalign(0)

        github_label = Gtk.Label(label="GitHub")
        github_label.set_xalign(1)
        github_label.set_markup('<a href="{}">GitHub</a>'.format(GITHUB_URL))
        github_label.set_cursor(Gdk.Cursor.new_from_name("pointer"))
        github_label.connect("activate-link", lambda _, uri: webbrowser.open(uri) or True)

        footer.append(version_label)
        footer.append(github_label)

        self.main_box.append(footer)
        self.set_child(scrolled)