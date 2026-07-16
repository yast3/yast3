"""Language settings tab for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from mast.core.i18n import _
from mast.core.languages import (
    get_current_language,
    get_use_utf8,
    save_language_settings,
    LanguageInfo,
    LocaleItem,
    build_locale_install_command,
)
from mast.qt6.command.action import CommandAction


class LanguageSettings(QWidget):
    language_installed = Signal()

    def __init__(self, locales: list[LocaleItem], parent: QWidget | None = None):
        super().__init__(parent)
        self._all_locales = locales
        self._setup_ui()
        self._load_languages()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.setFixedWidth(250)
        form_layout.addRow(_("Language"), self.language_combo)

        self.utf8_checkbox = QCheckBox()
        form_layout.addRow(_("Use UTF-8"), self.utf8_checkbox)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_language)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _load_languages(self) -> None:
        try:
            locale_map = {loc.code: loc for loc in self._all_locales}

            sorted_locales = sorted(
                self._all_locales,
                key=lambda x: x.name
            )

            for loc in sorted_locales:
                self.language_combo.addItem(loc.name, loc.code)

            current_lang = get_current_language()
            index = self.language_combo.findData(current_lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

            self.utf8_checkbox.setChecked(get_use_utf8())
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load languages: {0}").format(str(e)))

    def _is_locale_installed(self, locale_code: str) -> bool:
        return any(loc.code == locale_code and loc.installed for loc in self._all_locales)

    def save_language(self) -> None:
        lang_code = self.language_combo.currentData()
        use_utf8 = self.utf8_checkbox.isChecked()

        if not lang_code:
            QMessageBox.warning(self, _("Error"), _("Please select a language."))
            return

        if not self._is_locale_installed(lang_code):
            locale = next((loc for loc in self._all_locales if loc.code == lang_code), None)
            if locale:
                self._install_language_and_save(locale, lang_code, use_utf8)
            else:
                QMessageBox.warning(self, _("Error"), _("Language '{0}' not found.").format(lang_code))
            return

        self._save_language_settings(lang_code, use_utf8)

    def _install_language_and_save(self, locale: LocaleItem, lang_code: str, use_utf8: bool) -> None:
        self.current_action = CommandAction(
            text=_("Install"),
            running_text=_("Installing..."),
            dialog_title=_("Install Language"),
            command=build_locale_install_command(lang_code),
            success_output=_("Language '{0}' installed successfully.").format(locale.name),
            parent=self,
        )
        self.current_action.action_finished.connect(
            lambda success, error, stdout: self._on_install_finished(success, lang_code, use_utf8)
        )
        self.current_action.start_action()

    def _on_install_finished(self, success: bool, lang_code: str, use_utf8: bool) -> None:
        if success:
            for loc in self._all_locales:
                if loc.code == lang_code:
                    loc.installed = True
                    break
            self.language_installed.emit()
            self._save_language_settings(lang_code, use_utf8)

    def _save_language_settings(self, lang_code: str, use_utf8: bool) -> None:
        status, message = save_language_settings(lang_code, use_utf8=use_utf8)

        if status == "ok":
            locale = next((loc for loc in self._all_locales if loc.code == lang_code), None)
            lang_name = locale.name if locale else lang_code
            QMessageBox.information(
                self,
                _("Success"),
                _("Language changed successfully to '{0}'. Changes will take effect after logout.").format(lang_name),
            )
            window = self.window()
            if window:
                window.close()
        elif status == "permission_denied":
            QMessageBox.critical(
                self, _("Error"), _("Permission denied. Root permission required.")
            )
        elif status == "pkexec_failed":
            QMessageBox.critical(
                self, _("Error"), _("Authentication failed or pkexec not available.")
            )
        else:
            QMessageBox.critical(
                self, _("Error"), _("Failed to set language: {0}").format(message)
            )
