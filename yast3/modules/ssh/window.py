"""UI components for the SSH module."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from yast3.i18n import _
from yast3.modules.ssh.hosts import HostsTab
from yast3.modules.ssh.keys import KeysTab


class SSHWindow(QMainWindow):
    closed = Signal()  # Signal emitted when window is closed

    def __init__(self):
        super().__init__()
        self.resize(960, 640)
        
        

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Hosts tab
        self.hosts_tab = HostsTab()
        self.tab_widget.addTab(self.hosts_tab, _("Hosts"))

        # Keys tab
        self.keys_tab = KeysTab()
        self.tab_widget.addTab(self.keys_tab, _("Keys"))

    def closeEvent(self, event) -> None:
        """Handle window close event to destroy the window."""
        self.closed.emit()
        self.deleteLater()