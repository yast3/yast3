"""Cron tab UI component for managing cron jobs (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.cron import CronJob, load_cron_jobs, save_cron_jobs
from yast3.gtk4.cron.cron_edit_dialog import CronEditDialog


class CronTab(Gtk.Box):
    """Tab for managing cron jobs."""

    def __init__(self, user_mode: bool):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.user_mode = user_mode
        self.jobs: list[CronJob] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

        # Button bar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.add_btn = Gtk.Button(label=_("Add"))
        self.add_btn.connect("clicked", self._on_add_clicked)
        button_box.append(self.add_btn)

        self.edit_btn = Gtk.Button(label=_("Edit"))
        self.edit_btn.connect("clicked", self._on_edit_clicked)
        button_box.append(self.edit_btn)

        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.connect("clicked", self._on_delete_clicked)
        button_box.append(self.delete_btn)

        button_box.append(Gtk.Box())  # Spacer
        button_box.set_hexpand(True)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.append(button_box)

        # Create list view
        self._create_list_view()

        # Load jobs
        self._load_jobs()

    def _create_list_view(self) -> None:
        """Create the list view for cron jobs."""
        # Create list store
        self.list_store = Gtk.ListStore(bool, str, str, str, str, str, str)

        # Create tree view
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        # Enabled column
        enabled_renderer = Gtk.CellRendererToggle()
        enabled_renderer.connect("toggled", self._on_enabled_toggled)
        enabled_column = Gtk.TreeViewColumn(_("Enabled"), enabled_renderer, active=0)
        enabled_column.set_resizable(True)
        enabled_column.set_min_width(60)
        self.tree_view.append_column(enabled_column)

        # Minute column
        minute_renderer = Gtk.CellRendererText()
        minute_column = Gtk.TreeViewColumn(_("Minute"), minute_renderer, text=1)
        minute_column.set_resizable(True)
        minute_column.set_min_width(60)
        self.tree_view.append_column(minute_column)

        # Hour column
        hour_renderer = Gtk.CellRendererText()
        hour_column = Gtk.TreeViewColumn(_("Hour"), hour_renderer, text=2)
        hour_column.set_resizable(True)
        hour_column.set_min_width(60)
        self.tree_view.append_column(hour_column)

        # Day column
        day_renderer = Gtk.CellRendererText()
        day_column = Gtk.TreeViewColumn(_("Day"), day_renderer, text=3)
        day_column.set_resizable(True)
        day_column.set_min_width(60)
        self.tree_view.append_column(day_column)

        # Month column
        month_renderer = Gtk.CellRendererText()
        month_column = Gtk.TreeViewColumn(_("Month"), month_renderer, text=4)
        month_column.set_resizable(True)
        month_column.set_min_width(60)
        self.tree_view.append_column(month_column)

        # Weekday column
        weekday_renderer = Gtk.CellRendererText()
        weekday_column = Gtk.TreeViewColumn(_("Weekday"), weekday_renderer, text=5)
        weekday_column.set_resizable(True)
        weekday_column.set_min_width(60)
        self.tree_view.append_column(weekday_column)

        # Command column
        command_renderer = Gtk.CellRendererText()
        command_column = Gtk.TreeViewColumn(_("Command"), command_renderer, text=6)
        command_column.set_resizable(True)
        self.tree_view.append_column(command_column)

        # Selection
        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        # Add tree view to scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.append(scrolled)

    def _load_jobs(self) -> None:
        """Load cron jobs from file."""
        self.jobs.clear()
        self.list_store.clear()

        jobs, error = load_cron_jobs(self.user_mode)
        if error:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _(error))
            return

        self.jobs = jobs
        self._populate_list()

    def _populate_list(self) -> None:
        """Populate the list with cron jobs."""
        for job in self.jobs:
            command_text = job.command
            if job.comment:
                command_text += f"  {job.comment}"
            self.list_store.append([
                job.enabled,
                job.minute,
                job.hour,
                job.day,
                job.month,
                job.weekday,
                command_text,
            ])

    def _on_enabled_toggled(self, renderer, path) -> None:
        """Handle enabled toggle."""
        index = int(path)
        if 0 <= index < len(self.jobs):
            self.jobs[index].enabled = not self.jobs[index].enabled
            # Update the list store
            tree_iter = self.list_store.get_iter(path)
            self.list_store.set_value(tree_iter, 0, self.jobs[index].enabled)

    def _on_add_clicked(self, button: Gtk.Button) -> None:
        """Add a new cron job."""
        dialog = CronEditDialog(self.get_root())
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response_id) -> None:
        """Handle add dialog response."""
        if response_id == Gtk.ResponseType.OK:
            job = dialog.get_job()
            if job:
                self.jobs.append(job)
                self._populate_list()
        dialog.destroy()

    def _on_edit_clicked(self, button: Gtk.Button) -> None:
        """Edit the selected cron job."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a cron job to edit."))
            return

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        job = self.jobs[index]

        dialog = CronEditDialog(self.get_root(), job)
        dialog.connect("response", self._on_edit_dialog_response, index)
        dialog.present()

    def _on_edit_dialog_response(self, dialog, response_id, index: int) -> None:
        """Handle edit dialog response."""
        if response_id == Gtk.ResponseType.OK:
            new_job = dialog.get_job()
            if new_job:
                self.jobs[index] = new_job
                self._populate_list()
        dialog.destroy()

    def _on_delete_clicked(self, button: Gtk.Button) -> None:
        """Delete the selected cron job."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a cron job to delete."))
            return

        # Show confirmation dialog
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.format_secondary_text(_("Are you sure you want to delete this cron job?"))
        confirm_dialog.connect("response", self._on_delete_confirm_response, tree_iter)
        confirm_dialog.present()

    def _on_delete_confirm_response(self, dialog, response_id, tree_iter) -> None:
        """Handle delete confirmation response."""
        if response_id == Gtk.ResponseType.YES:
            path = self.list_store.get_path(tree_iter)
            index = int(path.to_string())
            self.jobs.pop(index)
            self.list_store.remove(tree_iter)
        dialog.destroy()

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Save cron jobs to file."""
        result = save_cron_jobs(self.jobs, self.user_mode)

        if result == "ok":
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Cron jobs saved successfully."))
        elif result == "permission_denied":
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Permission denied. Root permission required."))
        else:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Failed to save cron jobs."))

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        """Show a message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()