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


class LanguagesWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
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
        """Load available languages and current settings."""
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
        """Save the language settings."""
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
            self.close()
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

    def closeEvent(self, _event) -> None:
        """Handle window close event to destroy the window."""
        self.closed.emit()
        self.deleteLater()