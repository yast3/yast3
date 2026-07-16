"""Cron job manager widget."""

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

from mast.core.i18n import _
from mast.core.cron import load_root_cron, save_root_cron
from mast.qt6.cron.cron_edit_dialog import CronEditDialog


class Manager(QWidget):
    """Cron job manager widget."""

    def __init__(self, user_mode: bool, parent: QWidget | None = None):
        super().__init__(parent)
        self.user_mode = user_mode
        self.crontab: CronTab | None = None
        self._setup_ui()

    def load_cron(self) -> None:
        """Load cron jobs when tab is activated."""
        if self.crontab is None:
            self.crontab = CronTab(user=True) if self.user_mode else load_root_cron()
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
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self.delete_job)
        self.delete_btn.setEnabled(False)
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
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)

    def _on_selection_changed(self) -> None:
        selected = self.table.currentRow() >= 0
        self.edit_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)

    def _get_jobs(self) -> list[CronItem]:
        return list(self.crontab.crons)

    def populate_table(self) -> None:
        self.table.setRowCount(0)
        jobs = self._get_jobs()
        self.table.setRowCount(len(jobs))

        for row, job in enumerate(jobs):
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
        jobs = self._get_jobs()
        if 0 <= row < len(jobs):
            jobs[row].enable(state == Qt.CheckState.Checked.value)
            self.populate_row(row)

    def add_job(self) -> None:
        dialog = CronEditDialog(self)
        if dialog.exec():
            job_data = dialog.get_job_data()
            if job_data:
                minute, hour, day, month, weekday, command, comment = job_data
                new_job = self.crontab.new(command=command, comment=comment)
                new_job.setall(minute, hour, day, month, weekday)
                new_job.enable(True)
                self.populate_table()

    def edit_job(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a cron job to edit."))
            return

        jobs = self._get_jobs()
        job = jobs[current_row]
        dialog = CronEditDialog(self, job)
        if dialog.exec():
            job_data = dialog.get_job_data()
            if job_data:
                minute, hour, day, month, weekday, command, comment = job_data
                job.setall(minute, hour, day, month, weekday)
                job.command = command
                job.comment = comment
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
            jobs = self._get_jobs()
            job_to_delete = jobs[current_row]
            self.crontab.remove(job_to_delete)
            self.table.removeRow(current_row)

    def populate_row(self, row: int) -> None:
        jobs = self._get_jobs()
        if 0 <= row < len(jobs):
            job = jobs[row]

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
        try:
            if self.user_mode:
                self.crontab.write()
            else:
                if not save_root_cron(self.crontab):
                    raise Exception("Failed to save")
            QMessageBox.information(self, _("Success"), _("Cron jobs saved successfully."))
        except Exception:
            QMessageBox.critical(
                self, _("Error"), _("Permission denied. Root permission required.")
            )
