"""UI components for the Packages module."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

from yast3.core.i18n import _


class PackagesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("Packages"))

        # 2. 必须创建一个 核心Widget 填充中央区域
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.btn = QPushButton(_("Packages"))
        layout.addWidget(self.btn)

        # 3. 将其设为中心部件
        self.setCentralWidget(central_widget)