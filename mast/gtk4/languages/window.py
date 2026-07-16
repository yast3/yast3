"""UI components for the Languages module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.languages import get_all_locales, LocaleItem
from mast.gtk4.languages.settings import LanguageSettingsTab
from mast.gtk4.languages.manager import LocaleManager


class LanguagesWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(640, 480)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)

        self.notebook = Gtk.Notebook()

        self._all_locales = get_all_locales()

        settings_tab = LanguageSettingsTab(self._all_locales)
        settings_tab.connect("language-installed", self._on_language_installed)
        self.notebook.append_page(settings_tab, Gtk.Label(label=_("System Language")))

        locale_tab = LocaleManager(self._all_locales)
        self.notebook.append_page(locale_tab, Gtk.Label(label=_("Language Management")))

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)
        self.present()

    def _on_language_installed(self, widget) -> None:
        pages = self.notebook.get_n_pages()
        for i in range(pages):
            child = self.notebook.get_nth_page(i)
            if isinstance(child, LocaleManager):
                child.refresh_locales()
                break
