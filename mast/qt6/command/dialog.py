"""Command output dialog used by command action widgets."""

from __future__ import annotations

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _


class CommandOutputDialog(QDialog):
    """Dialog that shows command output during long-running operations."""

    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 420)

        layout = QVBoxLayout(self)

        self.status_label = QLabel(_("Running command, please wait..."))
        layout.addWidget(self.status_label)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        layout.addWidget(self.output)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        layout.addWidget(self.progress)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.close_btn = QPushButton(_("Close"))
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

    def append_output(self, line: str) -> None:
        if not line:
            return
        self.output.appendPlainText(line)

    def set_finished(self, success: bool) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.close_btn.setEnabled(True)
        if success:
            self.status_label.setText(_("Command completed successfully."))
        else:
            self.status_label.setText(_("Command failed. See output for details."))
