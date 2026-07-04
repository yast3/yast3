"""Qt6 Flatpak remote management widget."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from yast3.core.flatpak import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
)
from yast3.core.i18n import _


class _RemoteDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str,
        remote: FlatpakRemote | None = None,
        edit_mode: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_label = QLabel(remote.name if remote else "") if edit_mode else None
        self.name_input: QLineEdit | None = None

        if edit_mode:
            form.addRow(_("Name"), self.name_label)
        else:
            self.name_input = QLineEdit()
            form.addRow(_("Name"), self.name_input)

        self.url_input = QLineEdit()
        self.url_input.setText(remote.url if remote else "")
        form.addRow(_("URL"), self.url_input)

        if edit_mode:
            self.scope_value = remote.scope if remote else "system"
            form.addRow(_("Scope"), QLabel(self.scope_value))
            self.scope_combo = None
        else:
            self.scope_combo = QComboBox()
            self.scope_combo.addItem(_("System"), "system")
            self.scope_combo.addItem(_("User"), "user")
            form.addRow(_("Scope"), self.scope_combo)
            self.scope_value = "system"

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str, str]:
        if self.scope_combo is None:
            name = self.name_label.text() if self.name_label is not None else ""
            scope = self.scope_value
        else:
            name = self.name_input.text().strip() if self.name_input is not None else ""
            scope = str(self.scope_combo.currentData())

        url = self.url_input.text().strip()
        return name, url, scope


class FlatpakRemoteManager(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.remotes: list[FlatpakRemote] = []

        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self.add_remote)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton(_("Edit"))
        self.edit_btn.clicked.connect(self.edit_remote)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self.delete_remote)
        button_layout.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton(_("Refresh"))
        self.refresh_btn.clicked.connect(self.load_remotes)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([_("Name"), _("URL"), _("Scope")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, self.table.fontMetrics().horizontalAdvance("M") * 18)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 90)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        self.load_remotes()

    def load_remotes(self) -> None:
        try:
            self.remotes = list_flatpak_remotes()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to load Flatpak remotes: {0}").format(str(e)))
            self.remotes = []

        self.populate_table()

    def populate_table(self) -> None:
        self.table.setRowCount(len(self.remotes))
        for row, remote in enumerate(self.remotes):
            self.table.setItem(row, 0, QTableWidgetItem(remote.name))
            self.table.setItem(row, 1, QTableWidgetItem(remote.url))
            self.table.setItem(row, 2, QTableWidgetItem(remote.scope))

    def add_remote(self) -> None:
        dialog = _RemoteDialog(self, _("Add Remote"), edit_mode=False)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name, url, scope = dialog.values()
        try:
            add_flatpak_remote(name, url, scope)
            QMessageBox.information(self, _("Success"), _("Remote added successfully."))
            self.load_remotes()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to add remote: {0}").format(str(e)))

    def edit_remote(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.remotes):
            QMessageBox.information(self, _("Information"), _("Please select a remote to edit."))
            return

        remote = self.remotes[row]
        dialog = _RemoteDialog(self, _("Edit"), remote=remote, edit_mode=True)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        _name, url, scope = dialog.values()
        try:
            modify_flatpak_remote_url(remote.name, url, scope)
            QMessageBox.information(self, _("Success"), _("Remote URL updated successfully."))
            self.load_remotes()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to update remote URL: {0}").format(str(e)))

    def delete_remote(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.remotes):
            QMessageBox.information(self, _("Information"), _("Please select a remote to delete."))
            return

        remote = self.remotes[row]
        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to delete remote '{0}'?").format(remote.name),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_flatpak_remote(remote.name, remote.scope)
            QMessageBox.information(self, _("Success"), _("Remote deleted successfully."))
            self.load_remotes()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to delete remote: {0}").format(str(e)))
