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
from yast3.qt6.cron.cron_tab import CronTab


class CronWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(960, 640)

        self.setWindowTitle(_("{} — YaST3").format(_("Cron")))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.user_tab = CronTab(user_mode=True)
        self.tab_widget.addTab(self.user_tab, _("User Cron Jobs"))

        self.root_tab = CronTab(user_mode=False)
        self.tab_widget.addTab(self.root_tab, _("Root Cron Jobs"))

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()