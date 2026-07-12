"""Cron tab UI component for managing cron jobs."""

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

from crontab import CronItem, CronTab

from yast3.core.i18n import _
from yast3.core.cron import save_cron_jobs, load_root_cron
from yast3.qt6.cron.cron_edit_dialog import CronEditDialog


class CronTabTab(QWidget):
    """Tab for managing cron jobs."""

    def __init__(self, user_mode: bool, parent: QWidget | None = None):
        super().__init__(parent)
        self.user_mode = user_mode
        self.cron: CronTab = CronTab(user=True) if user_mode else load_root_cron()
        self.jobs: list[CronItem] = list(self.cron.crons)
        self._setup_ui()
        self.populate_table()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self.add_job)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton(_("Edit"))
        self.edit_btn.clicked.connect(self.edit_job)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self.delete_job)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_jobs)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "",
            _("Minute"),
            _("Hour"),
            _("Day"),
            _("Month"),
            _("Weekday"),
            _("Command"),
            _("Comment"),
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 30)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 60)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 60)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 60)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 60)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 60)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def populate_table(self) -> None:
        self.table.setRowCount(len(self.jobs))

        for row, job in enumerate(self.jobs):
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(job.is_enabled())
            checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
            enabled_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, enabled_widget)

            self.table.setItem(row, 1, QTableWidgetItem(str(job.minute)))
            self.table.setItem(row, 2, QTableWidgetItem(str(job.hour)))
            self.table.setItem(row, 3, QTableWidgetItem(str(job.day)))
            self.table.setItem(row, 4, QTableWidgetItem(str(job.month)))
            self.table.setItem(row, 5, QTableWidgetItem(str(job.dow)))

            cmd_item = QTableWidgetItem(job.command or "")
            if not job.is_enabled():
                cmd_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 6, cmd_item)

            comment_item = QTableWidgetItem(job.comment or "")
            if not job.is_enabled():
                comment_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 7, comment_item)

    def toggle_enabled(self, row: int, state: int) -> None:
        if 0 <= row < len(self.jobs):
            self.jobs[row].enable(state == Qt.CheckState.Checked.value)
            self.populate_row(row)

    def add_job(self) -> None:
        dialog = CronEditDialog(self)
        if dialog.exec():
            job = dialog.get_job()
            if job:
                self.jobs.append(job)
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.populate_row(row)

    def edit_job(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a cron job to edit."))
            return

        job = self.jobs[current_row]
        dialog = CronEditDialog(self, job)
        if dialog.exec():
            new_job = dialog.get_job()
            if new_job:
                self.jobs[current_row] = new_job
                self.populate_row(current_row)

    def delete_job(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a cron job to delete."))
            return

        reply = QMessageBox.question(
            self, _("Confirm"), _("Are you sure you want to delete this cron job?")
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.jobs.pop(current_row)
            self.table.removeRow(current_row)

    def populate_row(self, row: int) -> None:
        job = self.jobs[row]

        enabled_widget = QWidget()
        enabled_layout = QHBoxLayout(enabled_widget)
        enabled_layout.setContentsMargins(0, 0, 0, 0)
        enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox = QCheckBox()
        checkbox.setChecked(job.is_enabled())
        checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
        enabled_layout.addWidget(checkbox)
        self.table.setCellWidget(row, 0, enabled_widget)

        self.table.setItem(row, 1, QTableWidgetItem(str(job.minute)))
        self.table.setItem(row, 2, QTableWidgetItem(str(job.hour)))
        self.table.setItem(row, 3, QTableWidgetItem(str(job.day)))
        self.table.setItem(row, 4, QTableWidgetItem(str(job.month)))
        self.table.setItem(row, 5, QTableWidgetItem(str(job.dow)))

        cmd_item = QTableWidgetItem(job.command or "")
        if not job.is_enabled():
            cmd_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 6, cmd_item)

        comment_item = QTableWidgetItem(job.comment or "")
        if not job.is_enabled():
            comment_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 7, comment_item)

    def save_jobs(self) -> None:
        result = save_cron_jobs(self.jobs, self.user_mode)

        if result == "ok":
            QMessageBox.information(self, _("Success"), _("Cron jobs saved successfully."))
        elif result == "permission_denied":
            QMessageBox.critical(
                self, _("Error"), _("Permission denied. Root permission required.")
            )
        else:
            QMessageBox.critical(self, _("Error"), _("Failed to save cron jobs."))
