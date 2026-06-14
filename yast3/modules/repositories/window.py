"""UI components for the Repositories module."""

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

from yast3.modules.repositories.dialogs import RepoEditDialog
from yast3.modules.repositories.repos import RepoEntry, load_repos, save_repo_entry, delete_repo_entry


class RepositoriesWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(960, 540)
        self.statusBar().showMessage(_("System ready"))
        self.menuBar().addMenu(_("File"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self.add_repo)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton(_("Edit"))
        self.edit_btn.clicked.connect(self.edit_repo)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self.delete_repo)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "",
            _("Name"),
            _("URL"),
            _("Type"),
            _("Priority"),
            _("GPG Check")
        ])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 30)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, self.table.fontMetrics().horizontalAdvance("M") * 32)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 100)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 80)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 80)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        self.repo_entries: list[RepoEntry] = []
        self.load_repos()

    def load_repos(self) -> None:
        self.repo_entries.clear()
        self.table.setRowCount(0)

        try:
            self.repo_entries = load_repos()
        except PermissionError:
            QMessageBox.warning(self, _("Error"), _("Cannot read repository directory. Root permission required."))
            return

        self.populate_table()

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()

    def populate_table(self) -> None:
        self.table.setRowCount(len(self.repo_entries))

        for row, entry in enumerate(self.repo_entries):
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(entry.enabled)
            checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
            enabled_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, enabled_widget)

            self.table.setItem(row, 1, QTableWidgetItem(entry.name))
            self.table.setItem(row, 2, QTableWidgetItem(entry.url))
            self.table.setItem(row, 3, QTableWidgetItem(entry.type))
            self.table.setItem(row, 4, QTableWidgetItem(str(entry.priority)))
            self.table.setItem(row, 5, QTableWidgetItem(_("Yes") if entry.gpgcheck else _("No")))

    def toggle_enabled(self, row: int, state: int) -> None:
        if 0 <= row < len(self.repo_entries):
            self.repo_entries[row].enabled = state == Qt.CheckState.Checked.value
            self.save_single_entry(row)

    def add_repo(self) -> None:
        dialog = RepoEditDialog(self)
        if dialog.exec():
            values = dialog.get_values()
            name = values["name"]
            url = values["baseurl"] or values["mirrorlist"]
            
            if not name:
                QMessageBox.warning(self, _("Error"), _("Repository name is required."))
                return
            if not url:
                QMessageBox.warning(self, _("Error"), _("URL is required."))
                return

            filename = f"{name}.repo"
            new_entry = RepoEntry(
                name=name,
                filename=filename,
                **values
            )
            self.repo_entries.append(new_entry)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.populate_row(row)
            
            result = save_repo_entry(new_entry)
            if result != "ok":
                self.handle_save_error(result)

    def edit_repo(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a repository to edit."))
            return

        entry = self.repo_entries[current_row]
        dialog = RepoEditDialog(self, entry)
        if dialog.exec():
            values = dialog.get_values()
            name = values["name"]
            url = values["baseurl"] or values["mirrorlist"]
            
            if not name:
                QMessageBox.warning(self, _("Error"), _("Repository name is required."))
                return
            if not url:
                QMessageBox.warning(self, _("Error"), _("URL is required."))
                return

            self.repo_entries[current_row] = RepoEntry(
                name=name,
                filename=self.repo_entries[current_row].filename,
                **values
            )
            self.populate_row(current_row)
            
            result = save_repo_entry(self.repo_entries[current_row])
            if result != "ok":
                self.handle_save_error(result)

    def delete_repo(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a repository to delete."))
            return

        entry = self.repo_entries[current_row]
        reply = QMessageBox.question(self, _("Confirm"), _("Are you sure you want to delete repository '{}'?").format(entry.name))
        if reply == QMessageBox.StandardButton.Yes:
            result = delete_repo_entry(entry)
            if result == "ok":
                self.repo_entries.pop(current_row)
                self.table.removeRow(current_row)
            else:
                self.handle_save_error(result)

    def populate_row(self, row: int) -> None:
        entry = self.repo_entries[row]

        self.table.setCellWidget(row, 0, None)
        
        enabled_widget = QWidget()
        enabled_layout = QHBoxLayout(enabled_widget)
        enabled_layout.setContentsMargins(0, 0, 0, 0)
        enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox = QCheckBox()
        checkbox.setChecked(entry.enabled)
        checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
        enabled_layout.addWidget(checkbox)
        self.table.setCellWidget(row, 0, enabled_widget)

        self.table.setItem(row, 1, QTableWidgetItem(entry.name))
        self.table.setItem(row, 2, QTableWidgetItem(entry.url))
        self.table.setItem(row, 3, QTableWidgetItem(entry.type))
        self.table.setItem(row, 4, QTableWidgetItem(str(entry.priority)))
        self.table.setItem(row, 5, QTableWidgetItem(_("Yes") if entry.gpgcheck else _("No")))

    def save_single_entry(self, row: int) -> None:
        entry = self.repo_entries[row]
        result = save_repo_entry(entry)
        if result != "ok":
            self.handle_save_error(result)
            entry.enabled = not entry.enabled
            self.populate_row(row)

    def handle_save_error(self, result: str) -> None:
        if result == "permission_denied":
            QMessageBox.critical(self, _("Error"), _("Cannot write to repository directory. Root permission required."))
        elif result == "pkexec_failed":
            QMessageBox.critical(self, _("Error"), _("Authentication failed or pkexec not available."))
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save repository configuration."))