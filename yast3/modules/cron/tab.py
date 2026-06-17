"""Cron tab UI component for managing cron jobs."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
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

from yast3.i18n import _
from yast3.modules.cron.cron import CronJob, load_cron_jobs, save_cron_jobs, validate_cron_job, get_suggestions


class CronEditDialog(QDialog):
    """Dialog for editing or adding a cron job."""

    def __init__(self, parent: QWidget | None = None, job: CronJob | None = None):
        super().__init__(parent)
        self.job = job
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle(_("Edit Cron Job") if self.job else _("Add Cron Job"))
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        grid = QGridLayout()
        grid.setSpacing(8)

        self.minute_edit = QLineEdit()
        self.minute_edit.setPlaceholderText(_("0-59 or *"))
        self._add_field_row(grid, 0, _("Minute"), self.minute_edit, "minute")

        self.hour_edit = QLineEdit()
        self.hour_edit.setPlaceholderText(_("0-23 or *"))
        self._add_field_row(grid, 1, _("Hour"), self.hour_edit, "hour")

        self.day_edit = QLineEdit()
        self.day_edit.setPlaceholderText(_("1-31 or *"))
        self._add_field_row(grid, 2, _("Day"), self.day_edit, "day")

        self.month_edit = QLineEdit()
        self.month_edit.setPlaceholderText(_("1-12 or *"))
        self._add_field_row(grid, 3, _("Month"), self.month_edit, "month")

        self.weekday_edit = QLineEdit()
        self.weekday_edit.setPlaceholderText(_("0-7 or *"))
        self._add_field_row(grid, 4, _("Weekday"), self.weekday_edit, "weekday")

        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText(_("Command to execute"))
        grid.addWidget(QLabel(_("Command")), 5, 0)
        grid.addWidget(self.command_edit, 5, 1)

        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText(_("Optional comment"))
        grid.addWidget(QLabel(_("Comment")), 6, 0)
        grid.addWidget(self.comment_edit, 6, 1)

        layout.addLayout(grid)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.job:
            self.minute_edit.setText(self.job.minute)
            self.hour_edit.setText(self.job.hour)
            self.day_edit.setText(self.job.day)
            self.month_edit.setText(self.job.month)
            self.weekday_edit.setText(self.job.weekday)
            self.command_edit.setText(self.job.command)
            self.comment_edit.setText(self.job.comment)

    def _add_field_row(self, grid: QGridLayout, row: int, label: str, edit: QLineEdit, field_type: str) -> None:
        grid.addWidget(QLabel(label), row, 0)
        grid.addWidget(edit, row, 1)

        suggestions = get_suggestions(field_type)
        btn = QPushButton(_("Suggestions"))
        btn.clicked.connect(lambda: self._show_suggestions(edit, suggestions))
        grid.addWidget(btn, row, 2)

    def _show_suggestions(self, edit: QLineEdit, suggestions: list[str]) -> None:
        text = "\n".join(suggestions)
        QMessageBox.information(self, _("Suggestions"), text)

    def _on_ok(self) -> None:
        job = CronJob(
            minute=self.minute_edit.text().strip(),
            hour=self.hour_edit.text().strip(),
            day=self.day_edit.text().strip(),
            month=self.month_edit.text().strip(),
            weekday=self.weekday_edit.text().strip(),
            command=self.command_edit.text().strip(),
            comment=self.comment_edit.text().strip(),
            enabled=True,
        )

        valid, msg = validate_cron_job(job)
        if not valid:
            QMessageBox.warning(self, _("Validation Error"), msg)
            return

        self.job = job
        self.accept()

    def get_job(self) -> CronJob:
        return self.job


class CronTab(QWidget):
    """Tab for managing cron jobs."""

    def __init__(self, user_mode: bool, parent: QWidget | None = None):
        super().__init__(parent)
        self.user_mode = user_mode
        self.jobs: list[CronJob] = []
        self._setup_ui()

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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "",
            _("Minute"),
            _("Hour"),
            _("Day"),
            _("Month"),
            _("Weekday"),
            _("Command"),
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

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        self.load_jobs()

    def load_jobs(self) -> None:
        self.jobs.clear()
        self.table.setRowCount(0)

        jobs, error = load_cron_jobs(self.user_mode)
        if error:
            QMessageBox.warning(self, _("Error"), _(error))
            return

        self.jobs = jobs
        self.populate_table()

    def populate_table(self) -> None:
        self.table.setRowCount(len(self.jobs))

        for row, job in enumerate(self.jobs):
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setChecked(job.enabled)
            checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
            enabled_layout.addWidget(checkbox)
            self.table.setCellWidget(row, 0, enabled_widget)

            self.table.setItem(row, 1, QTableWidgetItem(job.minute))
            self.table.setItem(row, 2, QTableWidgetItem(job.hour))
            self.table.setItem(row, 3, QTableWidgetItem(job.day))
            self.table.setItem(row, 4, QTableWidgetItem(job.month))
            self.table.setItem(row, 5, QTableWidgetItem(job.weekday))

            command_text = job.command
            if job.comment:
                command_text += f"  {job.comment}"
            cmd_item = QTableWidgetItem(command_text)
            if not job.enabled:
                cmd_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 6, cmd_item)

    def toggle_enabled(self, row: int, state: int) -> None:
        if 0 <= row < len(self.jobs):
            self.jobs[row].enabled = state == Qt.CheckState.Checked.value
            self.populate_row(row)

    def add_job(self) -> None:
        dialog = CronEditDialog(self)
        if dialog.exec():
            job = dialog.get_job()
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

        self.table.setCellWidget(row, 0, None)

        enabled_widget = QWidget()
        enabled_layout = QHBoxLayout(enabled_widget)
        enabled_layout.setContentsMargins(0, 0, 0, 0)
        enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox = QCheckBox()
        checkbox.setChecked(job.enabled)
        checkbox.stateChanged.connect(lambda s, r=row: self.toggle_enabled(r, s))
        enabled_layout.addWidget(checkbox)
        self.table.setCellWidget(row, 0, enabled_widget)

        self.table.setItem(row, 1, QTableWidgetItem(job.minute))
        self.table.setItem(row, 2, QTableWidgetItem(job.hour))
        self.table.setItem(row, 3, QTableWidgetItem(job.day))
        self.table.setItem(row, 4, QTableWidgetItem(job.month))
        self.table.setItem(row, 5, QTableWidgetItem(job.weekday))

        command_text = job.command
        if job.comment:
            command_text += f"  {job.comment}"
        cmd_item = QTableWidgetItem(command_text)
        if not job.enabled:
            cmd_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 6, cmd_item)

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