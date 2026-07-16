"""Qt6 Flatpak remote management widget."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mast.core.flatpak import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
)
from mast.core.i18n import _
from mast.qt6.flatpak.remote_dialog import RemoteDialog


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
        dialog = RemoteDialog(self, _("Add Remote"), edit_mode=False)
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
        dialog = RemoteDialog(self, _("Edit"), remote=remote, edit_mode=True)
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
