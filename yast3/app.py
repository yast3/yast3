from __future__ import annotations
from .i18n import _
from .module import Module
from .modules import *

from typing import Iterable
from weakref import WeakSet

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


MODULES: tuple[Module, ...] = (
    GitModule(),
    HostsModule(),
    RepositoriesModule(),
    SSHClientModule(),
)



class ModuleWindow(QMainWindow):
    def __init__(self, module: Module, icon: QIcon) -> None:
        super().__init__()
        self.setWindowTitle(module.name)
        self.setWindowIcon(icon)
        self.resize(420, 240)

        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel(module.name, content)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 600;")

        description = QLabel(_("This settings module is not implemented yet."), content)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("color: palette(mid); font-size: 14px;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        self.setCentralWidget(content)


class MainWindow(QMainWindow):
    def __init__(self, modules: Iterable[Module] = MODULES) -> None:
        super().__init__()
        self.modules = tuple(modules)
        self.open_windows: WeakSet[ModuleWindow] = WeakSet()

        self.setWindowTitle("YaST3") # DO NOT TRANSLATE
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
            button = self._build_module_button(module, index)
            row, column = divmod(index, 4)
            grid.addWidget(button, row, column)

        scroll_area.setWidget(container)
        self.setCentralWidget(scroll_area)

    def _build_module_button(self, module: Module, index: int) -> QToolButton:
        icon = self._resolve_icon(module.icon_names)

        button = QToolButton()
        button.setText(module.name)
        if icon is not None:
            button.setIcon(icon)
        button.setIconSize(QSize(48, 48))
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setMinimumSize(180, 130)
        button.setAutoRaise(False)
        button.setStyleSheet(
            """
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
            """
        )
        button.clicked.connect(module.launch)
        return button

    def _resolve_icon(self, icon_names: tuple[str, ...]) -> QIcon | None:
        for name in icon_names:
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon

def main() -> int:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("YaST3")

    window = MainWindow()
    window.show()

    return app.exec()
