"""UI components for the Hostname module."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.modules.hostname import (
    get_current_hostname,
    set_hostname,
)


class HostnameWindow(QMainWindow):
    closed = Signal()  # Signal emitted when window is closed

    def __init__(self):
        super().__init__()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(8)

        # Hostname input
        input_layout = QHBoxLayout()
        label = QLabel(_("Hostname"))
        input_layout.addWidget(label)

        self.input = QLineEdit()
        self.input.setPlaceholderText(_("Enter hostname"))
        self.input.setFixedWidth(250)
        input_layout.addWidget(self.input)
        layout.addLayout(input_layout)

        # Button bar
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_hostname)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # Load current hostname
        self.load_hostname()

    def load_hostname(self) -> None:
        """Load the current system hostname."""
        try:
            current = get_current_hostname()
            self.input.setText(current)
        except FileNotFoundError:
            QMessageBox.warning(self, _("Error"), _("/etc/hostname not found."))
        except PermissionError:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Cannot read /etc/hostname. Root permission required."),
            )
        except Exception as e:
            QMessageBox.warning(
                self, _("Error"), _("Failed to load hostname: {0}").format(str(e))
            )

    def save_hostname(self) -> None:
        """Save the new hostname."""
        new_hostname = self.input.text().strip()

        if not new_hostname:
            QMessageBox.warning(self, _("Error"), _("Hostname cannot be empty."))
            return

        # Validate hostname (basic validation)
        if len(new_hostname) > 253:
            QMessageBox.warning(
                self, _("Error"), _("Hostname is too long (maximum 253 characters).")
            )
            return

        # Check for invalid characters
        invalid_chars = set(" /\\")
        if any(c in invalid_chars for c in new_hostname):
            QMessageBox.warning(
                self, _("Error"), _("Hostname contains invalid characters.")
            )
            return

        # Confirm with user
        try:
            current = get_current_hostname()
        except Exception:
            current = self.input.text()
        if current != new_hostname:
            reply = QMessageBox.question(
                self,
                _("Confirm"),
                _(
                    "Are you sure you want to change the hostname from '{0}' to '{1}'?"
                ).format(current, new_hostname),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Save the hostname change
        status, message = set_hostname(new_hostname)

        if status == "ok":
            QMessageBox.information(
                self,
                _("Success"),
                _("Hostname changed successfully to '{0}'.").format(new_hostname),
            )
            self.close()
        elif status == "permission_denied":
            QMessageBox.critical(
                self, _("Error"), _("Permission denied. Root permission required.")
            )
        elif status == "pkexec_failed":
            QMessageBox.critical(
                self, _("Error"), _("Authentication failed or pkexec not available.")
            )
        else:
            QMessageBox.critical(
                self, _("Error"), _("Failed to set hostname: {0}").format(message)
            )

    def closeEvent(self, _event) -> None:
        """Handle window close event to destroy the window."""
        self.closed.emit()
        self.deleteLater()