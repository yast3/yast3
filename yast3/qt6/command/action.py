"""Reusable command action with live output dialog."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget

from .dialog import CommandOutputDialog
from .worker import CommandWorker


class CommandAction(QAction):
    """Generic action that executes a command with an output dialog."""

    action_finished = Signal(bool, str, str)

    def __init__(
        self,
        text: str,
        running_text: str,
        dialog_title: str,
        command: list[str],
        success_output: str,
        auto_close_on_success: bool = False,
        auto_close_delay_ms: int = 500,
        parent: QObject | None = None,
    ):
        super().__init__(text, parent)

        self.default_text = text
        self.running_text = running_text
        self.dialog_title = dialog_title
        self.command = command
        self.success_output = success_output
        self.auto_close_on_success = auto_close_on_success
        self.auto_close_delay_ms = auto_close_delay_ms

        self.worker_thread: QThread | None = None
        self.worker: CommandWorker | None = None
        self.dialog: CommandOutputDialog | None = None

        self.triggered.connect(self.start_action)

    def start_action(self) -> None:
        if self.worker_thread is not None:
            return

        self.set_busy(True)

        dialog_parent: QWidget | None = None
        parent = self.parent()
        if isinstance(parent, QWidget):
            dialog_parent = parent
        else:
            active_window = QApplication.activeWindow()
            if isinstance(active_window, QWidget):
                dialog_parent = active_window

        self.dialog = CommandOutputDialog(self.dialog_title, dialog_parent)
        self.dialog.show()

        self.worker_thread = QThread(self)
        self.worker = CommandWorker(self.command)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.output.connect(self._on_output)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def is_running(self) -> bool:
        return self.worker_thread is not None

    def set_busy(self, busy: bool) -> None:
        self.setEnabled(not busy)
        self.setText(self.running_text if busy else self.default_text)

    def _on_output(self, line: str) -> None:
        if self.dialog is not None:
            self.dialog.append_output(line)

    def _on_finished(self, return_code: int, error: str, stdout: str = "") -> None:
        success = return_code == 0
        self.set_busy(False)

        if self.dialog is not None:
            self.dialog.set_finished(success)
            if success:
                self.dialog.append_output(self.success_output)
                if self.auto_close_on_success:
                    QTimer.singleShot(self.auto_close_delay_ms, self.dialog.close)
            elif error:
                self.dialog.append_output(error)

        self.action_finished.emit(success, error, stdout)
        self.worker_thread = None
        self.worker = None

