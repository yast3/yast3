"""Cron job edit dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.modules.cron import CronJob, validate_cron_job, get_suggestions


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

    def get_job(self) -> CronJob | None:
        return self.job