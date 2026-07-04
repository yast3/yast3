"""UI components for the Flatpak module."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yast3.core.flatpak import (
    install_flatpak_pkexec,
    is_flatpak_installed,
    remove_flatpak_pkexec,
)
from yast3.core.i18n import _
from yast3.qt6.flatpak.remote_manager import FlatpakRemoteManager


class FlatpakWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(760, 480)
        self.setWindowTitle(_("Flatpak Configuration — YaST3"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.install_box = QWidget()
        install_layout = QVBoxLayout(self.install_box)
        self.install_btn = QPushButton(_("Install Flatpak"))
        self.install_btn.clicked.connect(self.install_flatpak)
        install_layout.addWidget(self.install_btn)
        layout.addWidget(self.install_box)

        self.manage_box = QWidget()
        manage_layout = QVBoxLayout(self.manage_box)

        self.remote_manager = FlatpakRemoteManager(self)
        manage_layout.addWidget(self.remote_manager)

        danger_layout = QHBoxLayout()
        danger_layout.addStretch()
        self.remove_flatpak_btn = QPushButton(_("Remove Flatpak"))
        self.remove_flatpak_btn.clicked.connect(self.remove_flatpak)
        danger_layout.addWidget(self.remove_flatpak_btn)
        manage_layout.addLayout(danger_layout)

        layout.addWidget(self.manage_box)

        self.refresh_state()

    def refresh_state(self) -> None:
        installed = is_flatpak_installed()
        if installed:
            self.install_box.hide()
            self.manage_box.show()
            self.remote_manager.load_remotes()
        else:
            self.manage_box.hide()
            self.install_box.show()

    def install_flatpak(self) -> None:
        try:
            install_flatpak_pkexec()
            QMessageBox.information(self, _("Success"), _("Flatpak installed successfully."))
            self.refresh_state()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to install Flatpak: {0}").format(str(e)))

    def remove_flatpak(self) -> None:
        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to remove Flatpak?"),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            remove_flatpak_pkexec()
            QMessageBox.information(self, _("Success"), _("Flatpak removed successfully."))
            self.refresh_state()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to remove Flatpak: {0}").format(str(e)))

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()
