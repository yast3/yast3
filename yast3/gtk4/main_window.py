"""Main application window showing module buttons."""

from gi.repository import Gtk

from yast3.gtk4 import (
    CronModule,
    GitModule,
    HostnameModule,
    HostsModule,
    ProxyModule,
    RepositoriesModule,
    SSHClientModule,
)
from yast3.gtk4.module_button import ModuleButton


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.modules = (
            CronModule(),
            GitModule(),
            HostnameModule(),
            HostsModule(),
            ProxyModule(),
            RepositoriesModule(),
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
        self.set_child(scrolled)