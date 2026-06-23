"""UI components for the Cron module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.gtk4.cron.cron_tab import CronTab


class CronWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(960, 640)
        self.set_title(_("Cron Configuration — YaST3"))

        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)

        # Notebook for tabs
        self.notebook = Gtk.Notebook()

        # User cron tab
        self.user_tab = CronTab(user_mode=True)
        self.notebook.append_page(self.user_tab, Gtk.Label(label=_("User Cron Jobs")))

        # Root cron tab
        self.root_tab = CronTab(user_mode=False)
        self.notebook.append_page(self.root_tab, Gtk.Label(label=_("Root Cron Jobs")))

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)
        self.present()