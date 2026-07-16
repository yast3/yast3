"""Dialog for generating new SSH keys."""

import os
import subprocess

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
)

from mast.core.i18n import _
from mast.core.ssh import SSH_CONFIG_DIR


class GenerateKeyThread(QThread):
    """Thread for generating SSH key without blocking the UI."""

    finished = Signal(bool, str, str)  # success, private_key_path, error_message

    def __init__(
        self, key_path: str, key_type: str, key_size: int, comment: str, passphrase: str
    ):
        super().__init__()
        self.key_path = key_path
        self.key_type = key_type
        self.key_size = key_size
        self.comment = comment
        self.passphrase = passphrase

    def run(self) -> None:
        """Generate SSH key in background thread."""
        try:
            cmd = [
                "ssh-keygen",
                "-t",
                self.key_type,
                "-f",
                self.key_path,
                "-N",
                self.passphrase,
            ]

            if self.key_type == "rsa" and self.key_size:
                cmd.extend(["-b", str(self.key_size)])

            if self.comment:
                cmd.extend(["-C", self.comment])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.finished.emit(True, self.key_path, "")
            else:
                error = result.stderr.strip() if result.stderr else "Unknown error"
                self.finished.emit(False, "", error)
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "", "Key generation timed out")
        except Exception as e:
            self.finished.emit(False, "", str(e))


class GenerateKeyDialog(QDialog):
    """Dialog for generating a new SSH key."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Generate SSH Key"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self._keygen_thread: GenerateKeyThread | None = None

        layout = QVBoxLayout(self)

        # Key name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(_("Key Name:")))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(_("e.g., id_ed25519"))
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Key type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(_("Key Type:")))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["ED25519", "RSA", "ECDSA"])
        self.type_combo.setItemData(0, "ed25519")
        self.type_combo.setItemData(1, "rsa")
        self.type_combo.setItemData(2, "ecdsa")
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # RSA key size (only for RSA)
        self.size_layout = QHBoxLayout()
        self.size_label = QLabel(_("Key Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["4096 bits", "2048 bits", "3072 bits"])
        self.size_combo.setItemData(0, "4096")
        self.size_combo.setItemData(1, "2048")
        self.size_combo.setItemData(2, "3072")
        self.size_layout.addWidget(self.size_label)
        self.size_layout.addWidget(self.size_combo)
        self.size_layout.addStretch()
        layout.addLayout(self.size_layout)

        # Comment
        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel(_("Comment:")))
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText(_("e.g., user@hostname"))
        comment_layout.addWidget(self.comment_edit)
        layout.addLayout(comment_layout)

        # Passphrase
        passphrase_layout = QHBoxLayout()
        passphrase_layout.addWidget(QLabel(_("Passphrase:")))
        self.passphrase_edit = QLineEdit()
        self.passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        passphrase_layout.addWidget(self.passphrase_edit)
        layout.addLayout(passphrase_layout)

        # Info text
        info_label = QLabel(_("The key will be saved to {0}").format(SSH_CONFIG_DIR))
        info_label.setStyleSheet("color: palette(mid);")
        layout.addWidget(info_label)

        # Public key preview (after generation)
        self.public_key_label = QLabel(_("Public Key:"))
        self.public_key_label.setVisible(False)
        layout.addWidget(self.public_key_label)

        self.public_key_text = QPlainTextEdit()
        self.public_key_text.setReadOnly(True)
        self.public_key_text.setMaximumHeight(100)
        self.public_key_text.setVisible(False)
        layout.addWidget(self.public_key_text)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._generate)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(_("Generate"))
        layout.addWidget(self.buttons)

        # Initial state
        self._on_type_changed(0)

    def _on_type_changed(self, _index: int) -> None:
        """Handle key type selection change."""
        key_type = self.type_combo.currentData()
        # Show RSA size only for RSA keys
        self.size_label.setVisible(key_type == "rsa")
        self.size_combo.setVisible(key_type == "rsa")

    def _generate(self) -> None:
        """Start key generation."""
        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(self, _("Error"), _("Key name is required."))
            return

        # Validate name
        if not name.startswith("id_"):
            reply = QMessageBox.question(
                self,
                _("Confirm"),
                _("Key names starting with 'id_' are recommended. Continue anyway?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Check if key already exists
        key_path = os.path.join(SSH_CONFIG_DIR, name)
        if os.path.exists(key_path):
            QMessageBox.warning(
                self, _("Error"), _("A key with this name already exists.")
            )
            return

        key_type = self.type_combo.currentData()
        key_size = int(self.size_combo.currentData()) if key_type == "rsa" else 0
        comment = self.comment_edit.text().strip()
        passphrase = self.passphrase_edit.text()

        # Disable button during generation
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setEnabled(False)

        # Start generation in background thread
        self._keygen_thread = GenerateKeyThread(
            key_path, key_type, key_size, comment, passphrase
        )
        self._keygen_thread.finished.connect(self._on_generation_finished)
        self._keygen_thread.start()

    def _on_generation_finished(self, success: bool, key_path: str, error: str) -> None:
        """Handle key generation completion."""
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setEnabled(True)

        if success:
            # Show public key
            public_key_path = key_path + ".pub"
            try:
                with open(public_key_path, "r") as f:
                    public_key = f.read().strip()

                self.public_key_label.setVisible(True)
                self.public_key_text.setVisible(True)
                self.public_key_text.setPlainText(public_key)

                QMessageBox.information(
                    self, _("Success"), _("SSH key generated successfully.")
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(
                    self, _("Error"), _("Failed to read public key: {0}").format(str(e))
                )
                self.reject()
        else:
            QMessageBox.critical(
                self, _("Error"), _("Failed to generate SSH key: {0}").format(error)
            )