"""UI components for the Languages module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.languages import (
    get_current_language,
    get_use_utf8,
    build_languages_map,
    save_language_settings,
    LanguageInfo,
)
from yast3.gtk4.languages.locale_manager import LocaleManager


class LanguageSettingsTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        language_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label = Gtk.Label(label=_("Language"))
        label.set_size_request(100, -1)
        label.set_halign(Gtk.Align.START)
        language_box.append(label)

        self.language_combo = Gtk.ComboBoxText()
        self.language_combo.set_hexpand(True)
        language_box.append(self.language_combo)

        self.append(language_box)

        utf8_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label = Gtk.Label(label=_("Use UTF-8"))
        label.set_size_request(100, -1)
        label.set_halign(Gtk.Align.START)
        utf8_box.append(label)

        self.utf8_switch = Gtk.Switch()
        utf8_box.append(self.utf8_switch)

        self.append(utf8_box)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.append(button_box)

        self._load_languages()

    def _load_languages(self) -> None:
        try:
            languages_map = build_languages_map()
            self._language_info: dict[str, LanguageInfo] = languages_map

            sorted_languages = sorted(
                languages_map.items(),
                key=lambda x: x[1].name_english
            )

            for code, info in sorted_languages:
                self.language_combo.append(code, info.name)

            current_lang = get_current_language()
            if current_lang in self._language_info:
                self.language_combo.set_active_id(current_lang)

            self.utf8_switch.set_active(get_use_utf8())
        except Exception as e:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Failed to load languages: {0}").format(str(e)))

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        lang_code = self.language_combo.get_active_id()
        use_utf8 = self.utf8_switch.get_active()

        if not lang_code:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Please select a language."))
            return

        status, message = save_language_settings(lang_code, use_utf8=use_utf8)

        if status == "ok":
            info = self._language_info.get(lang_code)
            lang_name = info.name if info else lang_code
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Language changed successfully to '{0}'. Changes will take effect after logout.").format(lang_name))
            window = self.get_root()
            if window:
                window.close()
        elif status == "permission_denied":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Permission denied. Root permission required."))
        elif status == "pkexec_failed":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Authentication failed or pkexec not available."))
        else:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Failed to set language: {0}").format(message))

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


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

        settings_tab = LanguageSettingsTab()
        self.notebook.append_page(settings_tab, Gtk.Label(label=_("Language")))

        locale_tab = LocaleManager()
        self.notebook.append_page(locale_tab, Gtk.Label(label=_("Locale Management")))

        self.main_box.append(self.notebook)

        self.set_child(self.main_box)
        self.present()