"""Main application window showing module buttons."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QMainWindow,
    QScrollArea,
    QToolButton,
    QWidget,
)

from yast3.module import Module
from yast3.modules import (
    CronModule,
    GitModule,
    HostnameModule,
    HostsModule,
    RepositoriesModule,
    SSHClientModule,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.modules = (
            CronModule(),
            GitModule(),
            HostnameModule(),
            HostsModule(),
            RepositoriesModule(),
            SSHClientModule(),
        )

        self.setWindowTitle("YaST3")  # DO NOT TRANSLATE
        self.resize(960, 640)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget(scroll_area)
        grid = QGridLayout(container)
        grid.setContentsMargins(32, 32, 32, 32)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(24)

        for index, module in enumerate(self.modules):
            button = self._build_module_button(module)
            row, column = divmod(index, 4)
            grid.addWidget(button, row, column)

        scroll_area.setWidget(container)
        self.setCentralWidget(scroll_area)

    def _build_module_button(self, module: Module) -> QToolButton:
        icon = self._resolve_icon(module.icon_names)

        button = QToolButton()
        button.setText(module.name)
        if icon is not None:
            button.setIcon(icon)
        button.setIconSize(QSize(48, 48))
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setMinimumSize(180, 130)
        button.setAutoRaise(False)
        button.setStyleSheet("""
            QToolButton {
                border: 1px solid palette(midlight);
                border-radius: 12px;
                padding: 16px;
                font-size: 15px;
                font-weight: 500;
            }
            QToolButton:hover {
                background: palette(alternate-base);
            }
            """)
        button.clicked.connect(module.launch)
        return button

    def _resolve_icon(self, icon_names: tuple[str, ...]) -> QIcon | None:
        for name in icon_names:
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon
