"""UI components for the Security module."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


def build_ui(parent: QWidget | None = None) -> QWidget:
    """Build and return the root widget for this module."""
    root = QWidget(parent)
    layout = QVBoxLayout(root)

    title = QLabel("Security", root)
    title.setObjectName("moduleTitle")

    description = QLabel("UI placeholder for the Security module.", root)
    description.setWordWrap(True)

    layout.addWidget(title)
    layout.addWidget(description)
    layout.addStretch()
    return root
