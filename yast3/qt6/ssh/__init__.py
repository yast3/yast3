"""SSH client configuration module package - Qt6 GUI."""

import os
import stat

from PySide6.QtWidgets import QMessageBox

from yast3.core.i18n import _
from yast3.core.ssh import check_ssh_permissions, fix_ssh_permissions
from yast3.qt6.module import Module
from yast3.qt6.ssh.window import SSHWindow


class SSHClientModule(Module):
    def __init__(self):
        super().__init__(_("SSH Client"), ("network-server", "network"), experimental=True)

    def _create_window(self):
        return SSHWindow()

    def launch(self, parent=None) -> None:
        super().launch(parent)
        self._check_and_fix_permissions()

    def _check_and_fix_permissions(self) -> None:
        issues = check_ssh_permissions()
        if not issues:
            return

        lines = []
        for issue in issues:
            name = os.path.basename(issue.path) or ".ssh"
            current = stat.filemode(issue.current_mode)
            expected = stat.filemode(issue.expected_mode)
            lines.append(f"  {name}: {current} → {expected}")

        detail = "\n".join(lines)

        reply = QMessageBox.warning(
            self.window,
            _("SSH Permission Warning"),
            _(
                "The following SSH items have insecure permissions:\n\n"
                "{0}\n\n"
                "Would you like to fix them now?"
            ).format(detail),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            failed = fix_ssh_permissions(issues)
            if failed:
                failed_names = "\n".join(
                    f"  {os.path.basename(p) or '.ssh'}" for p in failed
                )
                QMessageBox.critical(
                    self.window,
                    _("Error"),
                    _(
                        "Failed to fix permissions for the following items:\n\n" "{0}"
                    ).format(failed_names),
                )
            else:
                QMessageBox.information(
                    self.window,
                    _("Success"),
                    _("SSH permissions have been fixed successfully."),
                )


__all__ = ["SSHClientModule"]