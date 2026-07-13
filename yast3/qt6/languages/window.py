"""UI components for the Languages module (Qt6)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from yast3.core.i18n import _
from yast3.core.languages import (
    get_current_language,
    get_use_utf8,
    build_languages_map,
    save_language_settings,
    LanguageInfo,
)
from yast3.qt6.languages.locale_manager import LocaleManager


class LanguageSettingsTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        language_layout = QHBoxLayout()
        label = QLabel(_("Language"))
        language_layout.addWidget(label)

        self.language_combo = QComboBox()
        self.language_combo.setFixedWidth(250)
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)

        utf8_layout = QHBoxLayout()
        label = QLabel(_("Use UTF-8"))
        utf8_layout.addWidget(label)

        self.utf8_checkbox = QCheckBox()
        utf8_layout.addWidget(self.utf8_checkbox)
        layout.addLayout(utf8_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_language)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

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
                self.language_combo.addItem(info.name, code)

            current_lang = get_current_language()
            index = self.language_combo.findData(current_lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

            self.utf8_checkbox.setChecked(get_use_utf8())
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load languages: {0}").format(str(e)))

    def save_language(self) -> None:
        lang_code = self.language_combo.currentData()
        use_utf8 = self.utf8_checkbox.isChecked()

        if not lang_code:
            QMessageBox.warning(self, _("Error"), _("Please select a language."))
            return

        status, message = save_language_settings(lang_code, use_utf8=use_utf8)

        if status == "ok":
            info = self._language_info.get(lang_code)
            lang_name = info.name if info else lang_code
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


class LanguagesWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()

        self.resize(640, 480)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.settings_tab = LanguageSettingsTab()
        self.tab_widget.addTab(self.settings_tab, _("Language"))

        self.locale_tab = LocaleManager()
        self.tab_widget.addTab(self.locale_tab, _("Locale Management"))

    def closeEvent(self, _event) -> None:
        self.closed.emit()
        self.deleteLater()