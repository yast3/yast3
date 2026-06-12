from __future__ import annotations
from .module import Module
from .modules import *

from dataclasses import dataclass
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
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


MODULES: tuple[Module, ...] = (
    PackagesModule(),
)

FALLBACK_ICONS: tuple[QStyle.StandardPixmap, ...] = (
    QStyle.SP_ComputerIcon,
    QStyle.SP_DesktopIcon,
    QStyle.SP_DriveNetIcon,
    QStyle.SP_BrowserReload,
    QStyle.SP_MediaVolume,
    QStyle.SP_DialogResetButton,
    QStyle.SP_DirHomeIcon,
    QStyle.SP_FileDialogDetailedView,
    QStyle.SP_ArrowUp,
    QStyle.SP_ArrowForward,
    QStyle.SP_DriveHDIcon,
    QStyle.SP_MessageBoxWarning,
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

        description = QLabel("This settings page is not implemented yet.", content)
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

        self.setWindowTitle("YaST3")
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
        icon = self._resolve_icon(module.icon_names, FALLBACK_ICONS[index % len(FALLBACK_ICONS)])

        button = QToolButton()
        button.setText(module.name)
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
        button.clicked.connect(lambda checked=False, item=module, item_icon=icon: self.open_module_window(item, item_icon))
        return button

    def _resolve_icon(self, icon_names: tuple[str, ...], fallback: QStyle.StandardPixmap) -> QIcon:
        for name in icon_names:
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon

        return self.style().standardIcon(fallback)

    def open_module_window(self, module: Module, icon: QIcon) -> None:
        window = ModuleWindow(module, icon)
        window.show()
        window.activateWindow()
        self.open_windows.add(window)


def main() -> int:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("YaST3")

    window = MainWindow()
    window.show()

    return app.exec()
