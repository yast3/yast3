"""Dialog components for the SSH module."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.ssh import get_available_options


class SSHOptionEditDialog(QDialog):
    """Dialog for editing SSH config options."""

    def __init__(self, parent: QWidget | None = None, options: dict[str, str] = None):
        super().__init__(parent)
        self.setWindowTitle(_("Edit SSH Options"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.options = dict(options) if options else {}

        layout = QVBoxLayout(self)

        # Scroll area for options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.options_layout = QFormLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Available options combo
        self.available_options = get_available_options()

        # Add known options
        for key, desc in self.available_options:
            edit = QLineEdit(self.options.get(key, ""))
            edit.setPlaceholderText(desc)
            self.options_layout.addRow(QLabel(key), edit)
            edit.textChanged.connect(lambda text, k=key: self._update_option(k, text))

        # Add custom option section
        custom_layout = QHBoxLayout()
        self.custom_key_edit = QLineEdit()
        self.custom_key_edit.setPlaceholderText(_("Option name"))
        self.custom_value_edit = QLineEdit()
        self.custom_value_edit.setPlaceholderText(_("Option value"))
        add_btn = QPushButton(_("Add"))
        add_btn.clicked.connect(self._add_custom_option)
        custom_layout.addWidget(self.custom_key_edit)
        custom_layout.addWidget(self.custom_value_edit)
        custom_layout.addWidget(add_btn)
        layout.addLayout(custom_layout)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _update_option(self, key: str, value: str) -> None:
        """Update option value."""
        if value.strip():
            self.options[key] = value.strip()
        elif key in self.options:
            del self.options[key]

    def _add_custom_option(self) -> None:
        """Add a custom option."""
        key = self.custom_key_edit.text().strip()
        value = self.custom_value_edit.text().strip()

        if not key:
            QMessageBox.warning(self, _("Error"), _("Option name is required."))
            return

        # Check if already exists
        exists = any(k.lower() == key.lower() for k in self.options.keys())
        if exists:
            QMessageBox.warning(self, _("Error"), _("Option already exists."))
            return

        self.options[key] = value
        self.custom_key_edit.clear()
        self.custom_value_edit.clear()

        # Add to form
        edit = QLineEdit(value)
        self.options_layout.addRow(QLabel(key), edit)
        edit.textChanged.connect(lambda text, k=key: self._update_option(k, text))

    def get_options(self) -> dict[str, str]:
        """Get the current options."""
        return self.options


class SSHEditDialog(QDialog):
    """Dialog for adding or editing an SSH host entry."""

    def __init__(
        self,
        parent: QWidget | None = None,
        host: str = "",
        options: dict[str, str] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(_("Add/Edit SSH Host"))
        self.setMinimumWidth(500)

        self.options = dict(options) if options else {}

        layout = QVBoxLayout(self)

        # Host pattern
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel(_("Host Pattern:")))
        self.host_edit = QLineEdit(host)
        host_layout.addWidget(self.host_edit)
        layout.addLayout(host_layout)

        # Options button
        self.options_btn = QPushButton(_("Edit Options"))
        self.options_btn.clicked.connect(self._edit_options)
        layout.addWidget(self.options_btn)

        # Options summary
        self.options_summary = QLabel()
        self.options_summary.setStyleSheet("color: palette(mid);")
        self._update_options_summary()
        layout.addWidget(self.options_summary)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _edit_options(self) -> None:
        """Open options editing dialog."""
        dialog = SSHOptionEditDialog(self, self.options)
        if dialog.exec():
            self.options = dialog.get_options()
            self._update_options_summary()

    def _update_options_summary(self) -> None:
        """Update the options summary display."""
        if self.options:
            summary = _("Options: {0}").format(", ".join(self.options.keys()))
        else:
            summary = _("No options set")
        self.options_summary.setText(summary)

    def get_values(self) -> tuple[str, dict[str, str]]:
        """Get the host pattern and options."""
        return self.host_edit.text().strip(), self.options