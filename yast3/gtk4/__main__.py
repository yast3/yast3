"""Entry point for the GTK4 GUI application."""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from yast3.core.i18n import init_i18n
from yast3.gtk4.main_window import MainWindow


def main() -> int:
    # Initialize internationalization
    init_i18n()

    app = Gtk.Application(application_id="com.yast3.YaST3")

    def on_activate(app):
        win = MainWindow(application=app)
        win.show_all()

    app.connect("activate", on_activate)

    return app.run(None)


if __name__ == "__main__":
    raise SystemExit(main())