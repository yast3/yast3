"""UI components for the Cron module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.gtk4.cron.manager import Manager


class CronWindow(Gtk.ApplicationWindow):
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

        # User cron tab
        self.user_tab = Manager(user_mode=True)
        self.notebook.append_page(self.user_tab, Gtk.Label(label=_("User")))

        # System cron tab
        self.root_tab = Manager(user_mode=False)
        self.notebook.append_page(self.root_tab, Gtk.Label(label=_("System")))

        self.notebook.connect("switch-page", self._on_switch_page)
        self.user_tab.load_cron()

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)
        self.present()

    def _on_switch_page(self, notebook, page, page_num) -> None:
        """Load cron jobs when switching tabs."""
        if page_num == 0:
            self.user_tab.load_cron()
        else:
            self.root_tab.load_cron()