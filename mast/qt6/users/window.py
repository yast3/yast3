"""UI components for the Users & Groups module (Qt6)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.qt6.users.users_tab import UsersTab
from mast.qt6.users.groups_tab import GroupsTab


class UsersWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()

        self.resize(960, 640)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.users_tab = UsersTab()
        self.tab_widget.addTab(self.users_tab, _("Users"))

        self.groups_tab = GroupsTab()
        self.tab_widget.addTab(self.groups_tab, _("Groups"))

    def closeEvent(self, _event) -> None:
        self.closed.emit()
        self.deleteLater()