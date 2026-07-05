"""Reusable command action widget with live output dialog."""

from __future__ import annotations

import subprocess

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _


class CommandOutputDialog(QDialog):
    """Dialog that shows command output during long-running operations."""

    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 420)

        layout = QVBoxLayout(self)

        self.status_label = QLabel(_("Running command, please wait..."))
        layout.addWidget(self.status_label)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        layout.addWidget(self.progress)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.close_btn = QPushButton(_("Close"))
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

    def append_output(self, line: str) -> None:
        if not line:
            return
        self.output.appendPlainText(line)

    def set_finished(self, success: bool) -> None:
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.close_btn.setEnabled(True)
        if success:
            self.status_label.setText(_("Command completed successfully."))
        else:
            self.status_label.setText(_("Command failed. See output for details."))


class CommandWorker(QObject):
    """Run a command in a worker thread and stream output."""

    output = Signal(str)
    finished = Signal(int, str)

    def __init__(self, command: list[str]):
        super().__init__()
        self.command = command

    def run(self) -> None:
        self.output.emit("$ " + " ".join(self.command))

        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as e:
            self.finished.emit(-1, str(e))
            return

        lines: list[str] = []
        if process.stdout is not None:
            for raw_line in process.stdout:
                line = raw_line.rstrip()
                if line:
                    lines.append(line)
                    self.output.emit(line)

        return_code = process.wait()
        if return_code == 0:
            self.finished.emit(return_code, "")
            return

        error = "\n".join(lines[-20:]).strip() or _("Unknown error")
        self.finished.emit(return_code, error)


class CommandActionWidget(QWidget):
    """Generic button widget that executes command with output dialog."""

    action_finished = Signal(bool, str)

    def __init__(
        self,
        button_text: str,
        running_text: str,
        dialog_title: str,
        command: list[str],
        success_output: str,
        auto_close_on_success: bool = False,
        auto_close_delay_ms: int = 500,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.button_text = button_text
        self.running_text = running_text
        self.dialog_title = dialog_title
        self.command = command
        self.success_output = success_output
        self.auto_close_on_success = auto_close_on_success
        self.auto_close_delay_ms = auto_close_delay_ms

        self.worker_thread: QThread | None = None
        self.worker: CommandWorker | None = None
        self.dialog: CommandOutputDialog | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton(self.button_text)
        self.button.clicked.connect(self.start_action)
        layout.addWidget(self.button)

    def start_action(self) -> None:
        if self.worker_thread is not None:
            return

        self.set_busy(True)

        self.dialog = CommandOutputDialog(self.dialog_title, self.window())
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
        self.button.setEnabled(not busy)
        self.button.setText(self.running_text if busy else self.button_text)

    def _on_output(self, line: str) -> None:
        if self.dialog is not None:
            self.dialog.append_output(line)

    def _on_finished(self, return_code: int, error: str) -> None:
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

        self.action_finished.emit(success, error)
        self.worker_thread = None
        self.worker = None
