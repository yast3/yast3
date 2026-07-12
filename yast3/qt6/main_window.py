"""Main application window showing module buttons."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QStatusBar,
    QWidget,
)

from yast3.core import GITHUB_URL, __version__
from yast3.qt6 import (
    CronModule,
    DateTimeModule,
    FlatpakModule,
    GitModule,
    HostnameModule,
    HostsModule,
    LanguagesModule,
    ProxyModule,
    RepositoriesModule,
    ServicesModule,
    SnapshotsModule,
    SSHClientModule,
)
from yast3.qt6.module_button import ModuleButton


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.modules = (
            CronModule(),
            DateTimeModule(),
            FlatpakModule(),
            GitModule(),
            HostnameModule(),
            HostsModule(),
            LanguagesModule(),
            ProxyModule(),
            RepositoriesModule(),
            ServicesModule(),
            SnapshotsModule(),
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
            button = ModuleButton(module)
            row, column = divmod(index, 4)
            grid.addWidget(button, row, column)

        scroll_area.setWidget(container)
        self.setCentralWidget(scroll_area)

        status_bar = QStatusBar()
        version_label = QLabel(f"v{__version__}")
        github_label = QLabel(f'<a href="{GITHUB_URL}">GitHub</a>')
        github_label.setOpenExternalLinks(True)
        status_bar.addWidget(version_label)
        status_bar.addPermanentWidget(github_label)
        self.setStatusBar(status_bar)