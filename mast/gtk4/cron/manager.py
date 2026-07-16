"""Cron job manager widget (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from crontab import CronItem, CronTab

from mast.core.i18n import _
from mast.core.cron import load_root_cron, save_root_cron
from mast.gtk4.cron.cron_edit_dialog import CronEditDialog


class Manager(Gtk.Box):
    """Cron job manager widget."""

    def __init__(self, user_mode: bool):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.user_mode = user_mode
        self.cron: CronTab | None = None
        self._setup_ui()

    def load_cron(self) -> None:
        """Load cron jobs when tab is activated."""
        if self.cron is None:
            self.cron = CronTab(user=True) if self.user_mode else load_root_cron()
            self._populate_list()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.add_btn = Gtk.Button(label=_("Add"))
        self.add_btn.connect("clicked", self._on_add_clicked)
        button_box.append(self.add_btn)

        self.edit_btn = Gtk.Button(label=_("Edit"))
        self.edit_btn.connect("clicked", self._on_edit_clicked)
        self.edit_btn.set_sensitive(False)
        button_box.append(self.edit_btn)

        self.delete_btn = Gtk.Button(label=_("Delete"))
        self.delete_btn.connect("clicked", self._on_delete_clicked)
        self.delete_btn.set_sensitive(False)
        button_box.append(self.delete_btn)

        button_box.append(Gtk.Box())
        button_box.set_hexpand(True)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.append(button_box)

        self._create_list_view()

    def _create_list_view(self) -> None:
        """Create the list view for cron jobs."""
        self.list_store = Gtk.ListStore(bool, str, str, str, str, str, str, str)

        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        enabled_renderer = Gtk.CellRendererToggle()
        enabled_renderer.connect("toggled", self._on_enabled_toggled)
        enabled_column = Gtk.TreeViewColumn(_("Enabled"), enabled_renderer, active=0)
        enabled_column.set_resizable(True)
        enabled_column.set_min_width(60)
        self.tree_view.append_column(enabled_column)

        minute_renderer = Gtk.CellRendererText()
        minute_column = Gtk.TreeViewColumn(_("Minute"), minute_renderer, text=1)
        minute_column.set_resizable(True)
        minute_column.set_min_width(60)
        self.tree_view.append_column(minute_column)

        hour_renderer = Gtk.CellRendererText()
        hour_column = Gtk.TreeViewColumn(_("Hour"), hour_renderer, text=2)
        hour_column.set_resizable(True)
        hour_column.set_min_width(60)
        self.tree_view.append_column(hour_column)

        day_renderer = Gtk.CellRendererText()
        day_column = Gtk.TreeViewColumn(_("Day"), day_renderer, text=3)
        day_column.set_resizable(True)
        day_column.set_min_width(60)
        self.tree_view.append_column(day_column)

        month_renderer = Gtk.CellRendererText()
        month_column = Gtk.TreeViewColumn(_("Month"), month_renderer, text=4)
        month_column.set_resizable(True)
        month_column.set_min_width(60)
        self.tree_view.append_column(month_column)

        weekday_renderer = Gtk.CellRendererText()
        weekday_column = Gtk.TreeViewColumn(_("Weekday"), weekday_renderer, text=5)
        weekday_column.set_resizable(True)
        weekday_column.set_min_width(60)
        self.tree_view.append_column(weekday_column)

        command_renderer = Gtk.CellRendererText()
        command_column = Gtk.TreeViewColumn(_("Command"), command_renderer, text=6)
        command_column.set_resizable(True)
        self.tree_view.append_column(command_column)

        comment_renderer = Gtk.CellRendererText()
        comment_column = Gtk.TreeViewColumn(_("Comment"), comment_renderer, text=7)
        comment_column.set_resizable(True)
        self.tree_view.append_column(comment_column)

        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self._on_selection_changed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.append(scrolled)

    def _on_selection_changed(self, selection) -> None:
        """Handle selection change."""
        model, tree_iter = selection.get_selected()
        selected = tree_iter is not None
        self.edit_btn.set_sensitive(selected)
        self.delete_btn.set_sensitive(selected)

    def _get_jobs(self) -> list[CronItem]:
        return list(self.cron.crons)

    def _populate_list(self) -> None:
        """Populate the list with cron jobs."""
        self.list_store.clear()
        for job in self._get_jobs():
            self.list_store.append([
                job.is_enabled(),
                str(job.minute),
                str(job.hour),
                str(job.day),
                str(job.month),
                str(job.dow),
                job.command,
                job.comment,
            ])

    def _on_enabled_toggled(self, renderer, path) -> None:
        """Handle enabled toggle."""
        index = int(path)
        jobs = self._get_jobs()
        if 0 <= index < len(jobs):
            current_state = jobs[index].is_enabled()
            jobs[index].enable(not current_state)
            tree_iter = self.list_store.get_iter(path)
            self.list_store.set_value(tree_iter, 0, not current_state)

    def _on_add_clicked(self, button: Gtk.Button) -> None:
        """Add a new cron job."""
        dialog = CronEditDialog(self.get_root())
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response_id) -> None:
        """Handle add dialog response."""
        if response_id == Gtk.ResponseType.OK:
            job_data = dialog.get_job_data()
            if job_data:
                minute, hour, day, month, weekday, command, comment = job_data
                new_job = self.cron.new(command=command, comment=comment)
                new_job.setall(minute, hour, day, month, weekday)
                new_job.enable(True)
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
        jobs = self._get_jobs()
        job = jobs[index]

        dialog = CronEditDialog(self.get_root(), job)
        dialog.connect("response", self._on_edit_dialog_response, index)
        dialog.present()

    def _on_edit_dialog_response(self, dialog, response_id, index: int) -> None:
        """Handle edit dialog response."""
        if response_id == Gtk.ResponseType.OK:
            job_data = dialog.get_job_data()
            if job_data:
                minute, hour, day, month, weekday, command, comment = job_data
                jobs = self._get_jobs()
                job = jobs[index]
                job.setall(minute, hour, day, month, weekday)
                job.command = command
                job.comment = comment
                self._populate_list()
        dialog.destroy()

    def _on_delete_clicked(self, button: Gtk.Button) -> None:
        """Delete the selected cron job."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a cron job to delete."))
            return

        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.set_property("secondary-text", _("Are you sure you want to delete this cron job?"))
        confirm_dialog.connect("response", self._on_delete_confirm_response, tree_iter)
        confirm_dialog.present()

    def _on_delete_confirm_response(self, dialog, response_id, tree_iter) -> None:
        """Handle delete confirmation response."""
        if response_id == Gtk.ResponseType.YES:
            path = self.list_store.get_path(tree_iter)
            index = int(path.to_string())
            jobs = self._get_jobs()
            self.cron.remove(jobs[index])
            self.list_store.remove(tree_iter)
        dialog.destroy()

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Save cron jobs to file."""
        try:
            if self.user_mode:
                self.cron.write()
            else:
                if not save_root_cron(self.cron):
                    raise Exception("Failed to save")
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Cron jobs saved successfully."))
        except Exception:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Permission denied. Root permission required."))

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        """Show a message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
