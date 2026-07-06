"""UI components for the Flatpak module."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from yast3.core.flatpak import is_flatpak_installed
from yast3.core.i18n import _

from yast3.qt6.flatpak.install_action import InstallFlatpakAction
from yast3.qt6.flatpak.package_manager import FlatpakPackageManager
from yast3.qt6.flatpak.remote_manager import FlatpakRemoteManager
from yast3.qt6.flatpak.settings import FlatpakSettingsTab


class FlatpakWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(760, 480)
        self.setWindowTitle(_("Flatpak Configuration — YaST3"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(12)

        self.install_box = QWidget()
        install_layout = QVBoxLayout(self.install_box)
        self.install_action = InstallFlatpakAction(self)
        self.install_action.action_finished.connect(self._on_install_finished)
        self.install_button = QPushButton(self.install_action.text(), self.install_box)
        self.install_button.clicked.connect(self.install_action.trigger)
        self.install_action.changed.connect(self._sync_install_action_state)
        install_layout.addWidget(self.install_button)
        layout.addWidget(self.install_box)

        self.manage_box = QWidget()
        manage_layout = QVBoxLayout(self.manage_box)

        self.tabs = QTabWidget(self.manage_box)
        self.package_manager = FlatpakPackageManager(self.tabs)
        self.remote_manager = FlatpakRemoteManager(self.tabs)
        self.settings_tab = FlatpakSettingsTab(self.tabs)
        self.settings_tab.remove_action.action_finished.connect(self._on_remove_finished)
        self.tabs.addTab(self.package_manager, _("Packages"))
        self.tabs.addTab(self.remote_manager, _("Remotes"))
        self.tabs.addTab(self.settings_tab, _("Settings"))
        manage_layout.addWidget(self.tabs)

        layout.addWidget(self.manage_box)

        self._sync_install_action_state()

        self.refresh_state()

    def _sync_install_action_state(self) -> None:
        self.install_button.setText(self.install_action.text())
        self.install_button.setEnabled(self.install_action.isEnabled())

    def refresh_state(self) -> None:
        installed = is_flatpak_installed()
        if installed:
            self.install_box.hide()
            self.manage_box.show()
            self.package_manager.refresh()
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
        if self.install_action.is_running() or self.settings_tab.remove_action.is_running():
            QMessageBox.warning(
                self,
                _("Please wait"),
                _("A Flatpak operation is still running. Please wait for it to finish."),
            )
            event.ignore()
            return

        self.closed.emit()
        self.deleteLater()
