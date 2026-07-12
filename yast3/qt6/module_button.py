"""Qt6 button widget for launching a module."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QStyle, QToolButton

from yast3.core.i18n import _
from yast3.qt6.module import Module


class ModuleButton(QToolButton):
    """A button for launching a module window."""

    def __init__(self, module: Module) -> None:
        super().__init__()
        self._experimental_badge: QLabel | None = None
        self.setText(module.name)

        icon = self._resolve_icon(module.icon_names)
        if icon is not None:
            self.setIcon(icon)

        self.setIconSize(QSize(48, 48))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setMinimumSize(160, 120)
        self.setAutoRaise(False)


        if module.experimental:
            self._experimental_badge = self._create_experimental_badge()

        self.clicked.connect(module.launch)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._position_experimental_badge()

    def _create_experimental_badge(self) -> QLabel:
        badge = QLabel(self)
        badge.setObjectName("experimental-badge")
        badge.setToolTip(_("Experimental"))
        badge.setFixedSize(24, 24)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)


        icon = QIcon.fromTheme("dialog-warning")
        if icon.isNull():
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)

        badge.setPixmap(icon.pixmap(QSize(24, 24)))
        badge.raise_()
        self._position_experimental_badge()
        badge.show()
        return badge

    def _position_experimental_badge(self) -> None:
        if self._experimental_badge is None:
            return

        margin = 8
        x = self.width() - self._experimental_badge.width() - margin
        y = margin
        self._experimental_badge.move(x, y)

    @staticmethod
    def _resolve_icon(icon_names: tuple[str, ...]) -> QIcon | None:
        for name in icon_names:
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon

        return None