"""UI components for the Hosts module."""

from __future__ import annotations

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


HOSTS_FILE = "/etc/hosts"


class AddEditHostDialog(QDialog):
    """Dialog for adding or editing a host entry."""

    def __init__(self, parent: QWidget | None = None, ip: str = "", hostname: str = "", comment: str = ""):
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
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_values(self) -> tuple[str, str, str]:
        return self.ip_edit.text().strip(), self.hostname_edit.text().strip(), self.comment_edit.text().strip()


class HostsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.statusBar().showMessage(_("System ready"))
        self.menuBar().addMenu(_("File"))

        # Central widget with table
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

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
        # Tuple: (enabled, ip, hostname, comment, editable)
        self.hosts_entries: list[tuple[bool, str, str, str, bool]] = []
        self.load_hosts()

    def _looks_like_ip(self, string: str) -> bool:
        """Check if a string looks like an IP address."""
        if not string:
            return False
        
        # Check for IPv4 address (e.g., 127.0.0.1)
        parts = string.split('.')
        if len(parts) == 4:
            try:
                return all(0 <= int(p) <= 255 for p in parts)
            except ValueError:
                pass
        
        # Check for IPv6 address
        # IPv6 consists of hex characters (0-9, a-f, A-F) and colons
        # e.g., ::1, 2001:db8::1, fe80::1%eth0
        if ':' in string:
            # Remove interface suffix like %eth0 if present
            addr = string.split('%')[0]
            # Check if it's a valid IPv6 format
            # All characters should be hex digits or colons
            valid_chars = set('0123456789abcdefABCDEF:')
            if all(c in valid_chars for c in addr):
                # Additional check: should have at least one hex segment
                segments = addr.replace('::', ':').split(':')
                # Empty segments are ok for :: but there should be some content
                return any(s for s in segments) or addr == '::'
        
        return False

    def load_hosts(self) -> None:
        """Load hosts from /etc/hosts file."""
        self.hosts_entries.clear()
        self.table.setRowCount(0)

        try:
            with open(HOSTS_FILE, "r") as f:
                lines = f.readlines()
        except PermissionError:
            QMessageBox.warning(self, _("Error"), _("Cannot read {0}. Root permission required.").format(HOSTS_FILE))
            return
        except FileNotFoundError:
            QMessageBox.warning(self, _("Error"), _("{0} not found.").format(HOSTS_FILE))
            return

        for line in lines:
            original_line = line.rstrip("\n\r")
            stripped = original_line.strip()

            # Empty line - skip
            if not stripped:
                continue

            # Full comment line (no IP/hostname, just a comment)
            if stripped.startswith("#"):
                content = stripped.lstrip("#").strip()
                # Check if this looks like a valid hosts entry (has IP as first part)
                parts = content.split(None, 1)
                # If no parts or first part doesn't look like an IP address, treat as pure comment
                if not parts or not self._looks_like_ip(parts[0]):
                    # (enabled, ip, hostname, comment, editable=False)
                    self.hosts_entries.append((True, "", "", content, False))
                    continue
                
                # This is a disabled entry (commented-out hosts entry)
                ip = parts[0]
                hostname = parts[1] if len(parts) > 1 else ""
                # Check for inline comment (starts with # after whitespace)
                if hostname and hostname.lstrip().startswith("#"):
                    # (enabled, ip, hostname, comment, editable=False)
                    self.hosts_entries.append((False, ip, "", hostname.lstrip()[1:].strip(), False))
                else:
                    hostname_parts = hostname.split(None, 1) if hostname else [""]
                    host = hostname_parts[0] if hostname_parts else ""
                    comment = hostname_parts[1] if len(hostname_parts) > 1 else ""
                    # (enabled, ip, hostname, comment, editable=True)
                    self.hosts_entries.append((False, ip, host, comment.lstrip("#").strip() if comment else "", True))
                continue

            # Normal entry
            parts = stripped.split(None, 1)
            if parts and parts[0]:
                ip = parts[0]
                hostname = parts[1] if len(parts) > 1 else ""
                # Check for inline comment (starts with # after whitespace)
                if hostname and hostname.lstrip().startswith("#"):
                    # (enabled, ip, hostname, comment, editable=False)
                    self.hosts_entries.append((True, ip, "", hostname.lstrip()[1:].strip(), False))
                    continue
                hostname_parts = hostname.split(None, 1) if hostname else [""]
                host = hostname_parts[0] if hostname_parts else ""
                comment = hostname_parts[1] if len(hostname_parts) > 1 else ""
                # (enabled, ip, hostname, comment, editable=True)
                self.hosts_entries.append((True, ip, host, comment.lstrip("#").strip() if comment else "", True))

        self.populate_table()

    def populate_table(self) -> None:
        """Populate the table with host entries."""
        self.table.setRowCount(len(self.hosts_entries))

        for row, (enabled, ip, hostname, comment, editable) in enumerate(self.hosts_entries):
            # Enabled checkbox (only for editable entries)
            if editable:
                enabled_widget = QWidget()
                enabled_layout = QHBoxLayout(enabled_widget)
                enabled_layout.setContentsMargins(0, 0, 0, 0)
                enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox = QCheckBox()
                checkbox.setChecked(enabled)
                checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
                enabled_layout.addWidget(checkbox)
                self.table.setCellWidget(row, 0, enabled_widget)
            # For non-editable rows (pure comments), leave cell empty

            # IP Address
            self.table.setItem(row, 1, QTableWidgetItem(ip))

            # Hostname
            self.table.setItem(row, 2, QTableWidgetItem(hostname))

            # Comment
            self.table.setItem(row, 3, QTableWidgetItem(comment))

    def toggle_enabled(self, row: int, state: int) -> None:
        """Toggle the enabled state of a host entry."""
        if 0 <= row < len(self.hosts_entries):
            _enabled, ip, hostname, comment, editable = self.hosts_entries[row]
            self.hosts_entries[row] = (state == Qt.CheckState.Checked.value, ip, hostname, comment, editable)

    def add_host(self) -> None:
        """Add a new host entry."""
        dialog = AddEditHostDialog(self)
        if dialog.exec():
            ip, hostname, comment = dialog.get_values()
            if ip and hostname:
                # (enabled, ip, hostname, comment, editable=True)
                self.hosts_entries.append((True, ip, hostname, comment, True))
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

        enabled, ip, hostname, comment, editable = self.hosts_entries[current_row]
        dialog = AddEditHostDialog(self, ip, hostname, comment)
        if dialog.exec():
            new_ip, new_hostname, new_comment = dialog.get_values()
            if new_ip and new_hostname:
                self.hosts_entries[current_row] = (enabled, new_ip, new_hostname, new_comment, editable)
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
        enabled, ip, hostname, comment, editable = self.hosts_entries[row]

        # Clear cell widget first
        self.table.setCellWidget(row, 0, None)
        
        # Enabled checkbox (only for editable entries)
        if editable:
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
            enabled_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, enabled_widget)

        self.table.setItem(row, 1, QTableWidgetItem(ip))
        self.table.setItem(row, 2, QTableWidgetItem(hostname))
        self.table.setItem(row, 3, QTableWidgetItem(comment))

    def save_hosts(self) -> None:
        """Save hosts to /etc/hosts file."""
        lines = []
        for enabled, ip, hostname, comment, editable in self.hosts_entries:
            if not editable:
                # Pure comment line - just write the comment
                lines.append("# " + comment)
                continue
            
            line = ""
            if not enabled:
                line += "# "
            line += ip + "\t" + hostname
            if comment:
                line += "\t# " + comment
            lines.append(line)

        # Add trailing newline
        content = "\n".join(lines) + "\n"

        try:
            with open(HOSTS_FILE, "w") as f:
                f.write(content)
            QMessageBox.information(self, _("Success"), _("Hosts file saved successfully."))
            self.statusBar().showMessage(_("Saved successfully"), 3000)
        except PermissionError:
            QMessageBox.critical(self, _("Error"), _("Cannot write to {0}. Root permission required.").format(HOSTS_FILE))
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to save hosts file: {0}").format(str(e)))