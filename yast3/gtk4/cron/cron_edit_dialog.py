"""Cron job edit dialog (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.cron import CronJob, validate_cron_job, get_suggestions


class CronEditDialog(Gtk.Dialog):
    """Dialog for editing or adding a cron job."""

    def __init__(self, parent, job: CronJob | None = None):
        super().__init__(
            title=_("Edit Cron Job") if job else _("Add Cron Job"),
            transient_for=parent,
            modal=True,
        )
        self.job = job
        self.result_job = None

        self.set_default_size(500, -1)

        # Add buttons
        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("OK"), Gtk.ResponseType.OK)

        # Content area
        content = self.get_content_area()
        content.set_spacing(8)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        # Grid for fields
        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(12)

        # Minute
        self.minute_entry = self._add_field_row(grid, 0, _("Minute"), _("0-59 or *"), "minute")

        # Hour
        self.hour_entry = self._add_field_row(grid, 1, _("Hour"), _("0-23 or *"), "hour")

        # Day
        self.day_entry = self._add_field_row(grid, 2, _("Day"), _("1-31 or *"), "day")

        # Month
        self.month_entry = self._add_field_row(grid, 3, _("Month"), _("1-12 or *"), "month")

        # Weekday
        self.weekday_entry = self._add_field_row(grid, 4, _("Weekday"), _("0-7 or *"), "weekday")

        # Command
        command_label = Gtk.Label(label=_("Command"))
        command_label.set_halign(Gtk.Align.START)
        grid.attach(command_label, 0, 5, 1, 1)
        self.command_entry = Gtk.Entry()
        self.command_entry.set_placeholder_text(_("Command to execute"))
        self.command_entry.set_hexpand(True)
        grid.attach(self.command_entry, 1, 5, 2, 1)

        # Comment
        comment_label = Gtk.Label(label=_("Comment"))
        comment_label.set_halign(Gtk.Align.START)
        grid.attach(comment_label, 0, 6, 1, 1)
        self.comment_entry = Gtk.Entry()
        self.comment_entry.set_placeholder_text(_("Optional comment"))
        self.comment_entry.set_hexpand(True)
        grid.attach(self.comment_entry, 1, 6, 2, 1)

        content.append(grid)

        # Connect OK button to validation
        ok_btn = self.get_widget_for_response(Gtk.ResponseType.OK)
        if ok_btn:
            ok_btn.connect("clicked", self._on_ok_clicked)

        # Load existing job data
        if self.job:
            self.minute_entry.set_text(self.job.minute)
            self.hour_entry.set_text(self.job.hour)
            self.day_entry.set_text(self.job.day)
            self.month_entry.set_text(self.job.month)
            self.weekday_entry.set_text(self.job.weekday)
            self.command_entry.set_text(self.job.command)
            self.comment_entry.set_text(self.job.comment)

    def _add_field_row(self, grid: Gtk.Grid, row: int, label: str, placeholder: str, field_type: str) -> Gtk.Entry:
        """Add a field row with label, entry, and suggestions button."""
        label_widget = Gtk.Label(label=label)
        label_widget.set_halign(Gtk.Align.START)
        grid.attach(label_widget, 0, row, 1, 1)

        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        grid.attach(entry, 1, row, 1, 1)

        suggestions_btn = Gtk.Button(label=_("Suggestions"))
        suggestions_btn.connect("clicked", self._on_suggestions_clicked, entry, field_type)
        grid.attach(suggestions_btn, 2, row, 1, 1)

        return entry

    def _on_suggestions_clicked(self, button: Gtk.Button, entry: Gtk.Entry, field_type: str) -> None:
        """Show suggestions for the field."""
        suggestions = get_suggestions(field_type)
        text = "\n".join(suggestions)
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Suggestions"),
        )
        dialog.format_secondary_text(text)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _on_ok_clicked(self, button: Gtk.Button) -> None:
        """Validate and accept the dialog."""
        job = CronJob(
            minute=self.minute_entry.get_text().strip(),
            hour=self.hour_entry.get_text().strip(),
            day=self.day_entry.get_text().strip(),
            month=self.month_entry.get_text().strip(),
            weekday=self.weekday_entry.get_text().strip(),
            command=self.command_entry.get_text().strip(),
            comment=self.comment_entry.get_text().strip(),
            enabled=True,
        )

        valid, msg = validate_cron_job(job)
        if not valid:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Validation Error"),
            )
            dialog.format_secondary_text(msg)
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
            return

        self.result_job = job
        self.response(Gtk.ResponseType.OK)

    def get_job(self) -> CronJob | None:
        """Get the resulting cron job."""
        return self.result_job