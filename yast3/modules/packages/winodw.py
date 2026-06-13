"""UI components for the Bluetooth module."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QWidget


class PackagesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.statusBar().showMessage(_("System ready"))
        self.menuBar().addMenu(_("File"))
        
        # 2. 必须创建一个 核心Widget 填充中央区域
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.btn = QPushButton(_("I am a button"))
        layout.addWidget(self.btn)
        
        # 3. 将其设为中心部件
        self.setCentralWidget(central_widget)