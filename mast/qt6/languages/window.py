"""UI components for the Languages module (Qt6)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.core.languages import get_all_locales
from mast.qt6.languages.settings import LanguageSettings
from mast.qt6.languages.manager import LocaleManager


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

        self._all_locales = get_all_locales()

        self.settings_tab = LanguageSettings(self._all_locales)
        self.settings_tab.language_installed.connect(self._on_language_installed)
        self.tab_widget.addTab(self.settings_tab, _("System Language"))

        self.locale_tab = LocaleManager(self._all_locales)
        self.tab_widget.addTab(self.locale_tab, _("Language Management"))

    def _on_language_installed(self) -> None:
        self.locale_tab.refresh_locales()

    def closeEvent(self, _event) -> None:
        self.closed.emit()
        self.deleteLater()
