"""Keys tab UI component for the SSH module."""

from __future__ import annotations

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
from yast3.modules.ssh.keys.generate_dialog import GenerateKeyDialog
from yast3.modules.ssh.keys.manager import KeyManager, KeyInfo


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
        
        # Store key info for easy access when copying/deleting
        self.key_list: list[KeyInfo] = []

    def _generate_new_key(self) -> None:
        """Open dialog to generate a new SSH key."""
        dialog = GenerateKeyDialog(self)
        if dialog.exec():
            self.load_keys()

    def load_keys(self) -> None:
        """Load SSH keys from ~/.ssh/ directory."""
        self.table.setRowCount(0)
        
        # Use KeyManager to get key list
        self.key_list = KeyManager.list_keys()

        # Populate table
        self.table.setRowCount(len(self.key_list))
        for row, key_info in enumerate(self.key_list):
            self.table.setItem(row, 0, QTableWidgetItem(key_info.name))
            self.table.setItem(row, 1, QTableWidgetItem(key_info.algorithm))
            self.table.setItem(row, 2, QTableWidgetItem(key_info.size))
            self.table.setItem(row, 3, QTableWidgetItem(key_info.fingerprint or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(key_info.comment or "-"))
            self.table.setItem(row, 5, QTableWidgetItem(_("Yes") if key_info.has_passphrase else _("No")))
            self.table.setItem(row, 6, QTableWidgetItem(_("Yes") if key_info.has_public else _("No")))
            self.table.setItem(row, 7, QTableWidgetItem(_("Yes") if key_info.has_private else _("No")))

    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        selected_indexes = self.table.selectedIndexes()
        if selected_indexes:
            row = selected_indexes[0].row()
            if 0 <= row < len(self.key_list):
                key_info = self.key_list[row]
                self.copy_key_btn.setEnabled(key_info.has_public)
                self.delete_key_btn.setEnabled(True)
                return

        self.copy_key_btn.setEnabled(False)
        self.delete_key_btn.setEnabled(False)

    def copy_selected_key(self) -> None:
        """Copy the public key of the selected key."""
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            return
        
        row = selected_indexes[0].row()
        if 0 <= row < len(self.key_list):
            key_info = self.key_list[row]
            content = KeyManager.get_public_key(key_info)
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
        if not (0 <= row < len(self.key_list)):
            return
        
        key_info = self.key_list[row]
        
        # Build message with what will be deleted
        files_to_delete = []
        if key_info.has_private:
            files_to_delete.append(key_info.name)
        if key_info.has_public:
            files_to_delete.append(key_info.name + '.pub')
        
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
        
        # Use KeyManager to delete the key
        success, errors = KeyManager.delete_key(key_info)
        
        if errors:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Failed to delete some files:\n\n{0}").format("\n".join(errors)),
            )
        else:
            QMessageBox.information(self, _("Success"), _("Key deleted successfully."))
            self.load_keys()
