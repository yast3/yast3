"""Command output dialog used by command action widgets."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from mast.core.i18n import _


class CommandOutputDialog(Gtk.Window):
    """Dialog that shows command output during long-running operations."""

    def __init__(self, title: str, parent: Gtk.Window | None = None):
        super().__init__(title=title, transient_for=parent, modal=True)
        self.set_default_size(760, 420)

        self._finished = False
        self._pulse_id: int | None = None

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        layout.set_margin_top(12)
        layout.set_margin_bottom(12)
        layout.set_margin_start(12)
        layout.set_margin_end(12)

        self.status_label = Gtk.Label(label=_("Running command, please wait..."))
        self.status_label.set_halign(Gtk.Align.START)
        layout.append(self.status_label)

        self.output_buffer = Gtk.TextBuffer()
        self.output_view = Gtk.TextView(buffer=self.output_buffer)
        self.output_view.set_editable(False)
        self.output_view.set_cursor_visible(False)
        self.output_view.set_monospace(True)
        self.output_view.set_vexpand(True)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.output_view)
        scrolled.set_vexpand(True)
        layout.append(scrolled)

        self.progress = Gtk.ProgressBar()
        layout.append(self.progress)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.append(Gtk.Box(hexpand=True))

        self.close_btn = Gtk.Button(label=_("Close"))
        self.close_btn.set_sensitive(False)
        self.close_btn.connect("clicked", lambda _button: self.close())
        btn_row.append(self.close_btn)

        layout.append(btn_row)
        self.set_child(layout)

        self.connect("close-request", self._on_close_request)

        self._pulse_id = GLib.timeout_add(120, self._pulse_progress)

    def append_output(self, line: str) -> None:
        if not line:
            return

        end_iter = self.output_buffer.get_end_iter()
        self.output_buffer.insert(end_iter, line + "\n")
        self.output_view.scroll_to_iter(self.output_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)

    def set_finished(self, success: bool) -> None:
        self._finished = True
        self._stop_pulse()
        self.progress.set_fraction(1.0)
        self.close_btn.set_sensitive(True)

        if success:
            self.status_label.set_text(_("Command completed successfully."))
        else:
            self.status_label.set_text(_("Command failed. See output for details."))

    def _on_close_request(self, _window) -> bool:
        # Keep dialog open while command is running, matching disabled close button behavior.
        return not self._finished

    def _pulse_progress(self) -> bool:
        if self._finished:
            return False

        self.progress.pulse()
        return True

    def _stop_pulse(self) -> None:
        if self._pulse_id is not None:
            GLib.source_remove(self._pulse_id)
            self._pulse_id = None
