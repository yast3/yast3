"""UI components for the Cron module."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.qt6.cron.manager import Manager

class CronWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(960, 640)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.user_tab = Manager(user_mode=True)
        self.tab_widget.addTab(self.user_tab, _("User"))

        self.root_tab = Manager(user_mode=False)
        self.tab_widget.addTab(self.root_tab, _("System"))

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.user_tab.load_cron()

    def _on_tab_changed(self, index: int) -> None:
        """Load cron jobs when switching tabs."""
        if index == 0:
            self.user_tab.load_cron()
        else:
            self.root_tab.load_cron()

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()