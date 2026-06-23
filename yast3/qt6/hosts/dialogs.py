"""Dialog components for the Hosts module."""

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _


class HostsEditDialog(QDialog):
    """Dialog for adding or editing a host entry."""

    def __init__(
        self,
        parent: QWidget | None = None,
        ip: str = "",
        hostname: str = "",
        comment: str = "",
    ):
        super().__init__(parent)
        self.setWindowTitle(_("Add/Edit Host Entry"))
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # IP address
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel(_("IP Address:")))
        self.ip_edit = QLineEdit(ip)
        ip_validator = QRegularExpressionValidator(QRegularExpression(r"^[\w.:]+$"))
        self.ip_edit.setValidator(ip_validator)
        ip_layout.addWidget(self.ip_edit)
        layout.addLayout(ip_layout)

        # Hostname
        hostname_layout = QHBoxLayout()
        hostname_layout.addWidget(QLabel(_("Hostname:")))
        self.hostname_edit = QLineEdit(hostname)
        hostname_layout.addWidget(self.hostname_edit)
        layout.addLayout(hostname_layout)

        # Comment
        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel(_("Comment:")))
        self.comment_edit = QLineEdit(comment)
        comment_layout.addWidget(self.comment_edit)
        layout.addLayout(comment_layout)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_values(self) -> tuple[str, str, str]:
        return (
            self.ip_edit.text().strip(),
            self.hostname_edit.text().strip(),
            self.comment_edit.text().strip(),
        )