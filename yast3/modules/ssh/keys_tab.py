"""Keys tab component for the SSH module."""

from __future__ import annotations

import os
import stat
import subprocess

from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import (
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from yast3.i18n import _
from yast3.modules.ssh.generate_dialog import GenerateKeyDialog
from yast3.modules.ssh.ssh import SSH_CONFIG_DIR


class KeyPair:
    """Represents an SSH key pair (private + public key)."""
    def __init__(self, name: str):
        self.name = name
        self.private_path = os.path.join(SSH_CONFIG_DIR, name)
        self.public_path = os.path.join(SSH_CONFIG_DIR, name + '.pub')
        self.has_private = os.path.exists(self.private_path)
        self.has_public = os.path.exists(self.public_path)
        # Get key info using ssh-keygen command
        self.size, self.algorithm, self.fingerprint, self.comment = self._get_key_info()
        self.permissions = self._get_permissions()
        self.has_passphrase = self._has_passphrase()

    def _get_key_info(self) -> tuple[str, str, str, str]:
        """Get key size, algorithm, fingerprint and comment using ssh-keygen."""
        size = "N/A"
        algorithm = "Unknown"
        fingerprint = ""
        comment = ""
        
        # Use public key file if available
        filepath = self.public_path if self.has_public else self.private_path
        
        if os.path.exists(filepath):
            try:
                result = subprocess.run(
                    ['ssh-keygen', '-l', '-f', filepath],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = result.stdout.strip()
                if output:
                    # Output format: "256 SHA256:xxx user@hostname (ED25519)"
                    parts = output.split()
                    if len(parts) >= 3:
                        size = parts[0]
                        fingerprint = parts[1]
                        # Algorithm is in parentheses at the end
                        if len(parts) > 3:
                            last_part = parts[-1]
                            if last_part.startswith('(') and last_part.endswith(')'):
                                algorithm = last_part[1:-1]
                            # Comment is everything between fingerprint and algorithm
                            comment = ' '.join(parts[2:-1])
            except Exception:
                # Fallback to file-based detection if ssh-keygen fails
                size, algorithm, comment = self._fallback_key_info()
        
        return (size, algorithm, fingerprint, comment)

    def _fallback_key_info(self) -> tuple[str, str, str]:
        """Fallback key detection using file content."""
        size = "N/A"
        algorithm = "Unknown"
        comment = ""
        
        filepath = self.public_path if self.has_public else self.private_path
        
        try:
            with open(filepath, 'r') as f:
                first_line = f.readline().strip()
            
            if first_line.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                algorithm = 'RSA'
            elif first_line.startswith('-----BEGIN DSA PRIVATE KEY-----'):
                algorithm = 'DSA'
            elif first_line.startswith('-----BEGIN EC PRIVATE KEY-----'):
                algorithm = 'EC'
            elif first_line.startswith('-----BEGIN OPENSSH PRIVATE KEY-----'):
                algorithm = 'OpenSSH'
            elif first_line.startswith('ssh-rsa '):
                algorithm = 'RSA'
            elif first_line.startswith('ssh-dss '):
                algorithm = 'DSA'
            elif first_line.startswith('ecdsa-sha2-'):
                algorithm = 'EC'
            elif first_line.startswith('ssh-ed25519 '):
                algorithm = 'ED25519'
            
            # Get comment from public key
            if self.has_public:
                with open(self.public_path, 'r') as f:
                    content = f.read().strip()
                    parts = content.split()
                    if len(parts) >= 3:
                        comment = ' '.join(parts[2:])
        except Exception:
            pass
        
        return (size, algorithm, comment)

    def _get_permissions(self) -> str:
        """Get file permissions."""
        if self.has_private:
            try:
                file_stat = os.stat(self.private_path)
                return stat.filemode(file_stat.st_mode)
            except Exception:
                pass
        if self.has_public:
            try:
                file_stat = os.stat(self.public_path)
                return stat.filemode(file_stat.st_mode)
            except Exception:
                pass
        return "???"

    def _has_passphrase(self) -> bool:
        """Check if the private key is encrypted (has passphrase)."""
        if self.has_private:
            try:
                with open(self.private_path, 'r') as f:
                    first_line = f.readline().strip()
                    # Check for encrypted private key markers
                    if first_line.startswith('-----BEGIN') and 'ENCRYPTED' in first_line:
                        return True
                    # OpenSSH format
                    if first_line.startswith('-----BEGIN OPENSSH PRIVATE KEY-----'):
                        # Read second line for encryption info
                        lines = f.readlines()
                        for line in lines[:5]:  # Check first few lines
                            if line.startswith('Proc-Type: 4,ENCRYPTED'):
                                return True
            except Exception:
                pass
        return False

    def get_public_key_content(self) -> str | None:
        """Get the content of the public key file."""
        if self.has_public:
            try:
                with open(self.public_path, 'r') as f:
                    return f.read().strip()
            except Exception:
                return None
        return None


class KeysTab(QWidget):
    """Keys tab for displaying SSH key files."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()
        self.load_keys()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Button bar
        button_layout = QHBoxLayout()
        self.new_key_btn = QPushButton(_("Add"))
        self.new_key_btn.clicked.connect(self._generate_new_key)
        button_layout.addWidget(self.new_key_btn)

        self.copy_key_btn = QPushButton(_("Copy Public Key"))
        self.copy_key_btn.clicked.connect(self.copy_selected_key)
        self.copy_key_btn.setEnabled(False)
        button_layout.addWidget(self.copy_key_btn)

        self.delete_key_btn = QPushButton(_("Delete"))
        self.delete_key_btn.clicked.connect(self.delete_selected_key)
        self.delete_key_btn.setEnabled(False)
        button_layout.addWidget(self.delete_key_btn)

        self.refresh_btn = QPushButton(_("Refresh"))
        self.refresh_btn.clicked.connect(self.load_keys)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Keys table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            _("Name"), _("Algorithm"), _("Size"), _("Fingerprint"), _("Comment"), _("Passphrase"), _("Public"), _("Private")
        ])
        
        # Column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 160)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 90)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 60)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 220)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 80)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 70)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 70)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Store key pairs for easy access when copying/deleting
        self.key_pairs: list[KeyPair] = []

    def _generate_new_key(self) -> None:
        """Open dialog to generate a new SSH key."""
        dialog = GenerateKeyDialog(self)
        if dialog.exec():
            self.load_keys()

    def load_keys(self) -> None:
        """Load SSH keys from ~/.ssh/ directory."""
        self.table.setRowCount(0)

        try:
            files = os.listdir(SSH_CONFIG_DIR)
        except FileNotFoundError:
            QMessageBox.warning(self, _("Error"), _("{0} directory not found.").format(SSH_CONFIG_DIR))
            return
        except PermissionError:
            QMessageBox.warning(self, _("Error"), _("Cannot read {0} directory.").format(SSH_CONFIG_DIR))
            return

        # Find private key files (without .pub extension)
        private_keys = set()
        for filename in files:
            filepath = os.path.join(SSH_CONFIG_DIR, filename)
            if os.path.isdir(filepath) or filename in ('known_hosts', 'config', 'authorized_keys'):
                continue
            
            # Skip public key files - we'll match them with their private keys
            if filename.endswith('.pub'):
                continue
            
            # Check if it looks like a key file
            if filename.endswith(('_rsa', '_dsa', '_ecdsa', '_ed25519')) or \
               filename.startswith('id_'):
                private_keys.add(filename)

        # Also check for .pub files that might not have corresponding private keys
        public_keys = set()
        for filename in files:
            if filename.endswith('.pub'):
                base_name = filename[:-4]  # Remove .pub
                filepath = os.path.join(SSH_CONFIG_DIR, filename)
                if os.path.isfile(filepath) and base_name not in private_keys:
                    public_keys.add(base_name)

        # Combine and create key pairs
        all_keys = sorted(private_keys.union(public_keys))
        self.key_pairs = [KeyPair(name) for name in all_keys]

        # Populate table
        self.table.setRowCount(len(self.key_pairs))
        for row, key_pair in enumerate(self.key_pairs):
            self.table.setItem(row, 0, QTableWidgetItem(key_pair.name))
            self.table.setItem(row, 1, QTableWidgetItem(key_pair.algorithm))
            self.table.setItem(row, 2, QTableWidgetItem(key_pair.size))
            self.table.setItem(row, 3, QTableWidgetItem(key_pair.fingerprint or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(key_pair.comment or "-"))
            self.table.setItem(row, 5, QTableWidgetItem(_("Yes") if key_pair.has_passphrase else _("No")))
            self.table.setItem(row, 6, QTableWidgetItem(_("Yes") if key_pair.has_public else _("No")))
            self.table.setItem(row, 7, QTableWidgetItem(_("Yes") if key_pair.has_private else _("No")))

    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        selected_indexes = self.table.selectedIndexes()
        if selected_indexes:
            row = selected_indexes[0].row()
            if 0 <= row < len(self.key_pairs):
                key_pair = self.key_pairs[row]
                self.copy_key_btn.setEnabled(key_pair.has_public)
                self.delete_key_btn.setEnabled(True)
                return

        self.copy_key_btn.setEnabled(False)
        self.delete_key_btn.setEnabled(False)

    def copy_selected_key(self) -> None:
        """Copy the public key of the selected key pair."""
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            return
        
        row = selected_indexes[0].row()
        if 0 <= row < len(self.key_pairs):
            key_pair = self.key_pairs[row]
            content = key_pair.get_public_key_content()
            if content:
                clipboard = QApplication.clipboard()
                clipboard.setText(content)
                QMessageBox.information(self, _("Success"), _("Public key copied to clipboard."))
            else:
                QMessageBox.warning(self, _("Error"), _("Cannot read public key file."))

    def delete_selected_key(self) -> None:
        """Delete the selected key pair."""
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            return
        
        row = selected_indexes[0].row()
        if not (0 <= row < len(self.key_pairs)):
            return
        
        key_pair = self.key_pairs[row]
        
        # Build message with what will be deleted
        files_to_delete = []
        if key_pair.has_private:
            files_to_delete.append(os.path.basename(key_pair.private_path))
        if key_pair.has_public:
            files_to_delete.append(os.path.basename(key_pair.public_path))
        
        reply = QMessageBox.question(
            self,
            _("Confirm Delete"),
            _("Are you sure you want to delete the following keys?\n\n{0}").format(
                "\n".join(files_to_delete)
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete files
        errors = []
        if key_pair.has_private:
            try:
                os.remove(key_pair.private_path)
            except Exception as e:
                errors.append(f"{key_pair.name}: {str(e)}")
        
        if key_pair.has_public:
            try:
                os.remove(key_pair.public_path)
            except Exception as e:
                errors.append(f"{key_pair.name}.pub: {str(e)}")
        
        if errors:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Failed to delete some files:\n\n{0}").format("\n".join(errors)),
            )
        else:
            QMessageBox.information(self, _("Success"), _("Key deleted successfully."))
            self.load_keys()