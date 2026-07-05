"""UI components for the Flatpak module."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from yast3.core.flatpak import is_flatpak_installed
from yast3.core.i18n import _
from yast3.qt6.flatpak.install_button import InstallFlatpakWidget
from yast3.qt6.flatpak.remove_button import RemoveFlatpakWidget
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
        self.install_widget = InstallFlatpakWidget(self.install_box)
        self.install_widget.action_finished.connect(self._on_install_finished)
        install_layout.addWidget(self.install_widget)
        layout.addWidget(self.install_box)

        self.manage_box = QWidget()
        manage_layout = QVBoxLayout(self.manage_box)

        self.remote_manager = FlatpakRemoteManager(self)
        manage_layout.addWidget(self.remote_manager)

        danger_layout = QHBoxLayout()
        danger_layout.addStretch()
        self.remove_widget = RemoveFlatpakWidget(self.manage_box)
        self.remove_widget.action_finished.connect(self._on_remove_finished)
        danger_layout.addWidget(self.remove_widget)
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

    def _on_install_finished(self, success: bool, error: str) -> None:
        if success:
            QMessageBox.information(self, _("Success"), _("Flatpak installed successfully."))
            self.refresh_state()
        else:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to install Flatpak: {0}").format(error or _("Unknown error")),
            )

    def _on_remove_finished(self, success: bool, error: str) -> None:
        if success:
            QMessageBox.information(self, _("Success"), _("Flatpak removed successfully."))
            self.refresh_state()
        else:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to remove Flatpak: {0}").format(error or _("Unknown error")),
            )

    def closeEvent(self, event) -> None:
        if self.install_widget.is_running() or self.remove_widget.is_running():
            QMessageBox.warning(
                self,
                _("Please wait"),
                _("A Flatpak operation is still running. Please wait for it to finish."),
            )
            event.ignore()
            return

        self.closed.emit()
        self.deleteLater()
