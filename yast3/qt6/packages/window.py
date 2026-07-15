"""UI components for the Packages module."""

from __future__ import annotations

import subprocess

from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from yast3.core.i18n import _


class PackagesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._launch_package_manager()

    def _launch_package_manager(self) -> None:
        try:
            subprocess.Popen(["myrlyn-sudo"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.close()
        except FileNotFoundError:
            self._show_error(_("Failed to launch package manager."))

    def _show_error(self, message: str) -> None:
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel(message))
        self.setCentralWidget(central_widget)