"""Settings tab for Flatpak module."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from yast3.qt6.flatpak.remove_action import RemoveFlatpakAction


class FlatpakSettingsTab(QWidget):
    """Settings UI for dangerous or advanced Flatpak operations."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addStretch()

        danger_layout = QHBoxLayout()
        danger_layout.addStretch()

        self.remove_action = RemoveFlatpakAction(self)
        self.remove_button = QPushButton(self.remove_action.text(), self)
        self.remove_button.clicked.connect(self.remove_action.trigger)
        self.remove_action.changed.connect(self._sync_remove_action_state)
        danger_layout.addWidget(self.remove_button)

        layout.addLayout(danger_layout)
        self._sync_remove_action_state()

    def _sync_remove_action_state(self) -> None:
        self.remove_button.setText(self.remove_action.text())
        self.remove_button.setEnabled(self.remove_action.isEnabled())
