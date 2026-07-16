"""Reusable command action with live output dialog."""

from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from mast.gtk4.command.dialog import CommandOutputDialog
from mast.gtk4.command.worker import CommandWorker


class CommandAction:
    """Generic action that executes a command with an output dialog."""

    def __init__(
        self,
        text: str,
        running_text: str,
        dialog_title: str,
        command: list[str],
        success_output: str,
        auto_close_on_success: bool = False,
        auto_close_delay_ms: int = 500,
        parent_window: Gtk.Window | None = None,
    ):
        self.default_text = text
        self.running_text = running_text
        self.dialog_title = dialog_title
        self.command = command
        self.success_output = success_output
        self.auto_close_on_success = auto_close_on_success
        self.auto_close_delay_ms = auto_close_delay_ms
        self.parent_window = parent_window

        self.worker: CommandWorker | None = None
        self.dialog: CommandOutputDialog | None = None
        self._busy = False

        self._changed_handlers: list[Callable[[], None]] = []
        self._finished_handlers: list[Callable[[bool, str], None]] = []

    def trigger(self, *_args) -> None:
        self.start_action()

    def start_action(self) -> None:
        if self.worker is not None:
            return

        self.set_busy(True)

        dialog_parent = self.parent_window if isinstance(self.parent_window, Gtk.Window) else None
        self.dialog = CommandOutputDialog(self.dialog_title, dialog_parent)
        self.dialog.present()

        self.worker = CommandWorker(
            self.command,
            on_output=self._emit_output,
            on_finished=self._emit_finished,
        )
        self.worker.start()

    def is_running(self) -> bool:
        return self.worker is not None

    def is_enabled(self) -> bool:
        return not self._busy

    def text(self) -> str:
        return self.running_text if self._busy else self.default_text

    def connect_changed(self, callback: Callable[[], None]) -> None:
        self._changed_handlers.append(callback)

    def connect_finished(self, callback: Callable[[bool, str, str], None]) -> None:
        self._finished_handlers.append(callback)

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        for callback in self._changed_handlers:
            callback()

    def _emit_output(self, line: str) -> None:
        GLib.idle_add(self._on_output, line)

    def _emit_finished(self, return_code: int, error: str, stdout: str = "") -> None:
        GLib.idle_add(self._on_finished, return_code, error, stdout)

    def _on_output(self, line: str) -> bool:
        if self.dialog is not None:
            self.dialog.append_output(line)
        return False

    def _on_finished(self, return_code: int, error: str, stdout: str = "") -> bool:
        success = return_code == 0
        self.set_busy(False)

        if self.dialog is not None:
            self.dialog.set_finished(success)
            if success:
                self.dialog.append_output(self.success_output)
                if self.auto_close_on_success:
                    GLib.timeout_add(self.auto_close_delay_ms, self._close_dialog)
            elif error:
                self.dialog.append_output(error)

        for callback in self._finished_handlers:
            callback(success, error, stdout)

        self.worker = None
        return False

    def _close_dialog(self) -> bool:
        if self.dialog is not None:
            self.dialog.close()
        return False
