"""About dialog for MaST GTK4 application."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core import GITHUB_URL, __version__, get_license_text
from mast.core.i18n import _


def show_about_dialog(parent: Gtk.Window) -> None:
    license_text = get_license_text()

    dialog = Gtk.AboutDialog(
        transient_for=parent,
        modal=True,
        program_name="MaST",
        version=__version__,
        website=GITHUB_URL,
        website_label=_("GitHub"),
        license=license_text,
    )
    dialog.present()