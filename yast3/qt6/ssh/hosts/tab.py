"""Hosts tab UI component for the SSH module."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.ssh import SSHConfigEntry
from yast3.qt6.ssh.dialogs import SSHEditDialog
from yast3.qt6.ssh.hosts.manager import HostManager


class HostsTab(QWidget):
    """Hosts tab for managing SSH config entries."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.entries: list[SSHConfigEntry] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Button bar
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self.add_host)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton(_("Edit"))
        self.edit_btn.clicked.connect(self.edit_host)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self.delete_host)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["", _("Host Pattern"), _("Options")])

        # Column widths
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(0, 30)  # Checkbox column
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(1, 200)  # Host pattern column
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )  # Options column

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        # Load config
        self.load_config()

    def load_config(self) -> None:
        """Load SSH config from ~/.ssh/config file."""
        self.entries.clear()
        self.table.setRowCount(0)

        entries, error = HostManager.load_config()
        if error:
            QMessageBox.warning(self, _("Error"), _(error))
            return

        self.entries = entries
        self.populate_table()

    def populate_table(self) -> None:
        """Populate the table with SSH config entries."""
        self.table.setRowCount(len(self.entries))

        for row, entry in enumerate(self.entries):
            # Enabled checkbox
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(entry.enabled)
            checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
            enabled_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, enabled_widget)

            # Host pattern
            host_item = QTableWidgetItem(entry.host)
            if HostManager.is_default(entry):
                host_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 1, host_item)

            # Options (show first 3 option names)
            option_names = list(entry.options.keys())[:3]
            options_text = ", ".join(option_names)
            if len(entry.options) > 3:
                options_text += _(" and {0} more").format(len(entry.options) - 3)
            self.table.setItem(row, 2, QTableWidgetItem(options_text))

    def toggle_enabled(self, row: int, state: int) -> None:
        """Toggle the enabled state of an entry."""
        if 0 <= row < len(self.entries):
            self.entries[row].enabled = state == Qt.CheckState.Checked.value

    def add_host(self) -> None:
        """Add a new SSH host entry."""
        dialog = SSHEditDialog(self)
        if dialog.exec():
            host, options = dialog.get_values()
            if host:
                self.entries.append(HostManager.create_entry(host, options))
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.populate_row(row)
            else:
                QMessageBox.warning(self, _("Error"), _("Host pattern is required."))

    def edit_host(self) -> None:
        """Edit the selected SSH host entry."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self, _("Information"), _("Please select a host entry to edit.")
            )
            return

        entry = self.entries[current_row]
        dialog = SSHEditDialog(self, entry.host, entry.options)
        if dialog.exec():
            new_host, new_options = dialog.get_values()
            if new_host:
                self.entries[current_row] = HostManager.update_entry(
                    entry, new_host, new_options
                )
                self.populate_row(current_row)
            else:
                QMessageBox.warning(self, _("Error"), _("Host pattern is required."))

    def delete_host(self) -> None:
        """Delete the selected SSH host entry."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self, _("Information"), _("Please select a host entry to delete.")
            )
            return

        entry = self.entries[current_row]
        if not HostManager.can_delete(entry):
            QMessageBox.warning(
                self, _("Error"), _("Cannot delete the default host entry.")
            )
            return

        reply = QMessageBox.question(
            self, _("Confirm"), _("Are you sure you want to delete this entry?")
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.entries.pop(current_row)
            self.table.removeRow(current_row)

    def populate_row(self, row: int) -> None:
        """Populate a single table row."""
        entry = self.entries[row]

        # Clear cell widget first
        self.table.setCellWidget(row, 0, None)

        # Enabled checkbox
        enabled_widget = QWidget()
        enabled_layout = QHBoxLayout(enabled_widget)
        enabled_layout.setContentsMargins(0, 0, 0, 0)
        enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox = QCheckBox()
        checkbox.setChecked(entry.enabled)
        checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
        enabled_layout.addWidget(checkbox)
        self.table.setCellWidget(row, 0, enabled_widget)

        host_item = QTableWidgetItem(entry.host)
        if HostManager.is_default(entry):
            host_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 1, host_item)

        option_names = list(entry.options.keys())[:3]
        options_text = ", ".join(option_names)
        if len(entry.options) > 3:
            options_text += _(" and {0} more").format(len(entry.options) - 3)
        self.table.setItem(row, 2, QTableWidgetItem(options_text))

    def save_config(self) -> None:
        """Save SSH config to ~/.ssh/config file."""
        result = HostManager.save_config(self.entries)

        if result == "ok":
            QMessageBox.information(
                self, _("Success"), _("SSH config saved successfully.")
            )
        elif result == "permission_denied":
            QMessageBox.critical(
                self, _("Error"), _("Cannot write to SSH config. Check permissions.")
            )
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save SSH config."))