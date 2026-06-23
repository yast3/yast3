"""Main application window showing module buttons."""

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.gtk4 import (
    CronModule,
    GitModule,
    HostnameModule,
    HostsModule,
    RepositoriesModule,
    SSHClientModule,
)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.modules = (
            CronModule(),
            GitModule(),
            HostnameModule(),
            HostsModule(),
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
        scrolled.add(self.main_box)

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
            button = self._build_module_button(module)
            row, column = divmod(index, 4)
            self.grid.attach(button, column, row, 1, 1)

        self.main_box.pack_start(self.grid, True, True, 0)
        self.add(scrolled)

        self.show_all()

    def _build_module_button(self, module: Module) -> Gtk.Button:
        """Create a button for a module."""
        button = Gtk.Button()
        button.set_size_request(180, 130)

        # Create button content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)

        # Try to get icon from theme
        icon_name = None
        icon_theme = Gtk.IconTheme.get_default()
        for name in module.icon_names:
            if icon_theme.has_icon(name):
                icon_name = name
                break

        if icon_name:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
            content_box.pack_start(icon, True, True, 0)
        else:
            # Use emoji as fallback
            emoji_label = Gtk.Label(label=module.emoji)
            content_box.pack_start(emoji_label, True, True, 0)

        # Module name
        name_label = Gtk.Label(label=module.name)
        content_box.pack_start(name_label, True, True, 0)

        button.add(content_box)

        button.connect("clicked", self._on_module_clicked, module)

        return button

    def _on_module_clicked(self, button: Gtk.Button, module: Module) -> None:
        """Handle module button click."""
        module.launch(self)