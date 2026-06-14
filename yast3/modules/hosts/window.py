"""UI components for the Hosts module."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from yast3.i18n import _
from yast3.modules.hosts.dialogs import HostsEditDialog
from yast3.modules.hosts.hosts import HostEntry, load_hosts, save_hosts


HOSTS_FILE = "/etc/hosts"


class HostsWindow(QMainWindow):
    closed = Signal()  # Signal emitted when window is closed

    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.statusBar().showMessage(_("System ready"))
        self.menuBar().addMenu(_("File"))

        # Central widget with table
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Button bar
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton(_("Edit"))
        self.edit_btn.clicked.connect(self.edit_host)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self.delete_host)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_hosts)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", _("IP Address"), _("Hostname"), _("Comment")])
        
        # Column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 30)  # Checkbox column (minimal)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 150)  # IP column (fits 255.255.255.255)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, self.table.fontMetrics().horizontalAdvance("M") * 32)  # ~32 chars
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Comment fills rest
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        # Load hosts
        self.hosts_entries: list[HostEntry] = []
        self.load_hosts()

    def load_hosts(self) -> None:
        """Load hosts from /etc/hosts file."""
        self.hosts_entries.clear()
        self.table.setRowCount(0)

        try:
            self.hosts_entries = load_hosts()
        except PermissionError:
            QMessageBox.warning(self, _("Error"), _("Cannot read {0}. Root permission required.").format(HOSTS_FILE))
            return
        except FileNotFoundError:
            QMessageBox.warning(self, _("Error"), _("{0} not found.").format(HOSTS_FILE))
            return

        self.populate_table()

    def closeEvent(self, event) -> None:
        """Handle window close event to destroy the window."""
        self.closed.emit()
        self.deleteLater()

    def populate_table(self) -> None:
        """Populate the table with host entries."""
        self.table.setRowCount(len(self.hosts_entries))

        for row, entry in enumerate(self.hosts_entries):
            # Enabled checkbox (only for editable entries)
            if entry.editable:
                enabled_widget = QWidget()
                enabled_layout = QHBoxLayout(enabled_widget)
                enabled_layout.setContentsMargins(0, 0, 0, 0)
                enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox = QCheckBox()
                checkbox.setChecked(entry.enabled)
                checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
                enabled_layout.addWidget(checkbox)
                self.table.setCellWidget(row, 0, enabled_widget)
            # For non-editable rows (pure comments), leave cell empty

            # IP Address
            self.table.setItem(row, 1, QTableWidgetItem(entry.ip))

            # Hostnames (join multiple hostnames with space)
            self.table.setItem(row, 2, QTableWidgetItem(" ".join(entry.hostnames)))

            # Comment
            self.table.setItem(row, 3, QTableWidgetItem(entry.comment))

    def toggle_enabled(self, row: int, state: int) -> None:
        """Toggle the enabled state of a host entry."""
        if 0 <= row < len(self.hosts_entries):
            entry = self.hosts_entries[row]
            entry.enabled = state == Qt.CheckState.Checked.value

    def add_host(self) -> None:
        """Add a new host entry."""
        dialog = HostsEditDialog(self)
        if dialog.exec():
            ip, hostname_str, comment = dialog.get_values()
            hostnames = hostname_str.split() if hostname_str else []
            if ip and hostnames:
                # Default comment separator for new entries
                comment_sep = "\t# " if comment else ""
                self.hosts_entries.append(HostEntry(
                    enabled=True,
                    ip=ip,
                    hostnames=hostnames,
                    comment_sep=comment_sep,
                    comment=comment,
                    editable=True
                ))
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.populate_row(row)
            else:
                QMessageBox.warning(self, _("Error"), _("IP address and hostname are required."))

    def edit_host(self) -> None:
        """Edit the selected host entry."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a host entry to edit."))
            return

        entry = self.hosts_entries[current_row]
        dialog = HostsEditDialog(self, entry.ip, " ".join(entry.hostnames), entry.comment)
        if dialog.exec():
            new_ip, new_hostname_str, new_comment = dialog.get_values()
            new_hostnames = new_hostname_str.split() if new_hostname_str else []
            if new_ip and new_hostnames:
                # Keep original comment_sep, or use default if comment changed
                new_comment_sep = entry.comment_sep if entry.comment_sep else ("\t# " if new_comment else "")
                self.hosts_entries[current_row] = HostEntry(
                    enabled=entry.enabled,
                    ip=new_ip,
                    hostnames=new_hostnames,
                    comment_sep=new_comment_sep,
                    comment=new_comment,
                    editable=entry.editable
                )
                self.populate_row(current_row)
            else:
                QMessageBox.warning(self, _("Error"), _("IP address and hostname are required."))

    def delete_host(self) -> None:
        """Delete the selected host entry."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a host entry to delete."))
            return

        reply = QMessageBox.question(self, _("Confirm"), _("Are you sure you want to delete this entry?"))
        if reply == QMessageBox.StandardButton.Yes:
            self.hosts_entries.pop(current_row)
            self.table.removeRow(current_row)

    def populate_row(self, row: int) -> None:
        """Populate a single table row."""
        entry = self.hosts_entries[row]

        # Clear cell widget first
        self.table.setCellWidget(row, 0, None)
        
        # Enabled checkbox (only for editable entries)
        if entry.editable:
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(entry.enabled)
            checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
            enabled_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, enabled_widget)

        self.table.setItem(row, 1, QTableWidgetItem(entry.ip))
        self.table.setItem(row, 2, QTableWidgetItem(" ".join(entry.hostnames)))
        self.table.setItem(row, 3, QTableWidgetItem(entry.comment))

    def save_hosts(self) -> None:
        """Save hosts to /etc/hosts file."""
        result = save_hosts(self.hosts_entries)
        
        if result == "ok":
            QMessageBox.information(self, _("Success"), _("Hosts file saved successfully."))
            self.statusBar().showMessage(_("Saved successfully"), 3000)
        elif result == "permission_denied":
            QMessageBox.critical(self, _("Error"), _("Cannot write to {0}. Root permission required.").format(HOSTS_FILE))
        elif result == "pkexec_failed":
            QMessageBox.critical(self, _("Error"), _("Authentication failed or pkexec not available."))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save hosts file."))